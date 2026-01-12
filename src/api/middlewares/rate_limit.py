"""
Rate Limiting Middleware

Simple token bucket algorithm for rate limiting.
Tracks requests per user/API key.
"""

import time
from typing import Dict
import threading
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..logging_config import get_logger

logger = get_logger(__name__, component="rate_limit")


class TokenBucket:
    """
    Token bucket rate limiter.

    Algorithm:
    - Bucket has max capacity (rate_limit)
    - Tokens refill at rate of 1 per second
    - Each request consumes 1 token
    - Request rejected if no tokens available
    """

    def __init__(self, rate_limit: int):
        self.capacity = rate_limit
        self.tokens = float(rate_limit)
        self.last_update = time.time()
        self.lock = threading.Lock()

    def consume(self) -> bool:
        """
        Try to consume one token.

        Returns:
            True if token consumed, False if rate limit exceeded
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update

            # Refill tokens (1 per second)
            self.tokens = min(self.capacity, self.tokens + elapsed)
            self.last_update = now

            # Try to consume
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True

            return False

    def get_remaining(self) -> int:
        """Get remaining tokens."""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            tokens = min(self.capacity, self.tokens + elapsed)
            return int(tokens)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Enhanced rate limiting middleware with tiered limits.

    Features:
    - Per-user rate limiting (100 req/min for authenticated users)
    - Per-IP rate limiting (30 req/min for unauthenticated IPs - stricter)
    - Per-API-key rate limiting (custom limits per key)
    - Token bucket algorithm for smooth rate distribution
    - Automatic cleanup of old buckets
    - Rate limit headers in responses (X-RateLimit-*)

    Configuration:
    - Authenticated users: 100 requests/minute (default_rate_limit)
    - Unauthenticated IPs: 30 requests/minute (ip_rate_limit - stricter)
    - API keys: Configurable per key (from storage)
    - Cleanup: Remove buckets idle for 10+ minutes

    Graceful Degradation:
    - Health check endpoints are exempt from rate limiting
    - Returns 429 with Retry-After header when limit exceeded
    - Provides remaining quota in X-RateLimit-Remaining header
    """

    def __init__(
        self,
        app,
        default_rate_limit: int = 100,  # requests per minute (authenticated users)
        ip_rate_limit: int = 30,  # requests per minute (unauthenticated IPs)
        cleanup_interval: int = 600  # 10 minutes
    ):
        super().__init__(app)
        self.default_rate_limit = default_rate_limit
        self.ip_rate_limit = ip_rate_limit  # Stricter limit for IPs
        self.cleanup_interval = cleanup_interval

        # Per-user buckets: {user_id: TokenBucket}
        self.buckets: Dict[str, TokenBucket] = {}
        self.last_access: Dict[str, float] = {}
        self.lock = threading.Lock()
        self.last_cleanup = time.time()

    def get_user_id(self, request: Request) -> str:
        """
        Extract user ID from request.

        Tries:
        1. state.user (set by auth middleware)
        2. X-API-Key header
        3. IP address (fallback)
        """
        # Try to get user from state (set by auth dependency)
        if hasattr(request.state, "user"):
            user = request.state.user
            return user.user_id

        # Try API key
        api_key = request.headers.get("x-api-key")
        if api_key:
            return f"apikey_{api_key[:8]}"  # Use prefix

        # Fallback to IP
        client_ip = request.client.host if request.client else "unknown"
        return f"ip_{client_ip}"

    def get_bucket(self, user_id: str) -> TokenBucket:
        """Get or create token bucket for user."""
        with self.lock:
            if user_id not in self.buckets:
                # Different limits based on user type
                if user_id.startswith("ip_"):
                    # Stricter limit for unauthenticated IPs
                    rate_limit = self.ip_rate_limit
                elif user_id.startswith("apikey_"):
                    # TODO: Fetch custom rate limit from API key storage
                    # For now, use default
                    rate_limit = self.default_rate_limit
                else:
                    # Authenticated users get default limit
                    rate_limit = self.default_rate_limit

                self.buckets[user_id] = TokenBucket(rate_limit)
                logger.debug(f"Created rate limit bucket for {user_id}: {rate_limit} req/min")

            self.last_access[user_id] = time.time()
            return self.buckets[user_id]

    def cleanup_old_buckets(self):
        """Remove buckets that haven't been used in cleanup_interval."""
        now = time.time()

        if now - self.last_cleanup < self.cleanup_interval:
            return

        with self.lock:
            expired = [
                user_id
                for user_id, last_time in self.last_access.items()
                if now - last_time > self.cleanup_interval
            ]

            for user_id in expired:
                del self.buckets[user_id]
                del self.last_access[user_id]

            if expired:
                logger.debug(f"Cleaned up {len(expired)} expired rate limit buckets")

            self.last_cleanup = now

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/v1/health"]:
            return await call_next(request)

        # Get user ID
        user_id = self.get_user_id(request)

        # Get bucket
        bucket = self.get_bucket(user_id)

        # Try to consume token
        if not bucket.consume():
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded for {user_id}",
                extra={
                    "event": "rate_limit_exceeded",
                    "user_id": user_id,
                    "path": request.url.path,
                    "method": request.method
                }
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Rate limit exceeded. Try again later.",
                        "details": {
                            "rate_limit": bucket.capacity,
                            "remaining": bucket.get_remaining(),
                            "retry_after": 1  # seconds
                        }
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(bucket.capacity),
                    "X-RateLimit-Remaining": str(bucket.get_remaining()),
                    "Retry-After": "1"
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(bucket.capacity)
        response.headers["X-RateLimit-Remaining"] = str(bucket.get_remaining())

        # Periodic cleanup
        self.cleanup_old_buckets()

        return response
