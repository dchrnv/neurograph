"""
NeuroGraph Performance Testing - Locust Load Tests
Version: v0.67.4

Run with:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000

Targets:
- 10,000+ requests/sec for REST API
- 1,000+ concurrent WebSocket connections
- p95 latency < 500ms
"""

import json
import random
from locust import HttpUser, TaskSet, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import websocket
import time


class NeuroGraphAPITasks(TaskSet):
    """
    Task set for REST API endpoints.

    Tests:
    - Health checks
    - Token CRUD operations
    - Grid queries
    - Authentication
    """

    def on_start(self):
        """Initialize test user - called once per user."""
        self.token_ids = []
        # Could authenticate here if needed
        # response = self.client.post("/api/v1/auth/login", json={...})

    @task(10)
    def health_check(self):
        """Health check - lightweight, high frequency."""
        self.client.get("/api/v1/health/live")

    @task(5)
    def health_ready(self):
        """Readiness check - more detailed."""
        self.client.get("/api/v1/health/ready")

    @task(20)
    def create_token(self):
        """Create token - core operation."""
        payload = {
            "coordinates": [
                random.uniform(-1.0, 1.0) for _ in range(8)
            ],
            "properties": {
                "type": "test",
                "timestamp": time.time()
            }
        }
        with self.client.post(
            "/api/v1/tokens",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                data = response.json()
                if "data" in data and "id" in data["data"]:
                    self.token_ids.append(data["data"]["id"])
                    response.success()
            else:
                response.failure(f"Failed to create token: {response.status_code}")

    @task(30)
    def read_token(self):
        """Read token - most frequent operation."""
        if self.token_ids:
            token_id = random.choice(self.token_ids)
            self.client.get(f"/api/v1/tokens/{token_id}")
        else:
            # Fall back to reading token 1 if we haven't created any yet
            self.client.get("/api/v1/tokens/1")

    @task(15)
    def list_tokens(self):
        """List tokens with pagination."""
        params = {
            "skip": random.randint(0, 100),
            "limit": random.choice([10, 20, 50])
        }
        self.client.get("/api/v1/tokens", params=params)

    @task(10)
    def grid_query(self):
        """Grid spatial query."""
        payload = {
            "coordinates": [random.uniform(-1.0, 1.0) for _ in range(8)],
            "radius": random.uniform(0.1, 2.0)
        }
        self.client.post("/api/v1/grid/query", json=payload)

    @task(5)
    def update_token(self):
        """Update token - less frequent."""
        if self.token_ids:
            token_id = random.choice(self.token_ids)
            payload = {
                "properties": {
                    "updated_at": time.time(),
                    "test_run": "performance"
                }
            }
            self.client.patch(f"/api/v1/tokens/{token_id}", json=payload)

    @task(2)
    def delete_token(self):
        """Delete token - least frequent."""
        if len(self.token_ids) > 10:  # Keep some tokens around
            token_id = self.token_ids.pop()
            self.client.delete(f"/api/v1/tokens/{token_id}")

    @task(8)
    def metrics_endpoint(self):
        """Prometheus metrics endpoint."""
        self.client.get("/api/v1/metrics")


class NeuroGraphAPIUser(FastHttpUser):
    """
    API user with FastHttpUser for better performance.

    Simulates user behavior:
    - Wait 1-3 seconds between requests
    - Execute tasks with weighted distribution
    """
    tasks = [NeuroGraphAPITasks]
    wait_time = between(1, 3)

    # Use FastHttpUser for better performance (gevent-based)
    # This allows more concurrent users per CPU


class NeuroGraphWebSocketUser(HttpUser):
    """
    WebSocket user for testing real-time connections.

    Tests:
    - WebSocket connection stability
    - Message throughput
    - Channel subscriptions
    """
    wait_time = between(5, 15)

    def on_start(self):
        """Connect to WebSocket."""
        self.ws = None
        self.connect_websocket()

    def on_stop(self):
        """Disconnect WebSocket."""
        if self.ws:
            self.ws.close()

    def connect_websocket(self):
        """Establish WebSocket connection."""
        try:
            ws_url = self.host.replace("http://", "ws://").replace("https://", "wss://")
            ws_url = f"{ws_url}/api/v1/ws"

            start_time = time.time()
            self.ws = websocket.create_connection(ws_url, timeout=10)

            # Track connection time
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(
                request_type="WebSocket",
                name="/api/v1/ws [connect]",
                response_time=total_time,
                response_length=0,
                exception=None,
                context={}
            )
        except Exception as e:
            events.request.fire(
                request_type="WebSocket",
                name="/api/v1/ws [connect]",
                response_time=0,
                response_length=0,
                exception=e,
                context={}
            )

    @task(1)
    def send_message(self):
        """Send WebSocket message."""
        if not self.ws:
            self.connect_websocket()
            return

        try:
            message = {
                "action": "subscribe",
                "channels": ["tokens", "metrics"]
            }

            start_time = time.time()
            self.ws.send(json.dumps(message))

            # Try to receive response
            try:
                response = self.ws.recv()
                total_time = int((time.time() - start_time) * 1000)

                events.request.fire(
                    request_type="WebSocket",
                    name="/api/v1/ws [send/recv]",
                    response_time=total_time,
                    response_length=len(response),
                    exception=None,
                    context={}
                )
            except websocket.WebSocketTimeoutError:
                # Timeout is okay, we might not get immediate response
                total_time = int((time.time() - start_time) * 1000)
                events.request.fire(
                    request_type="WebSocket",
                    name="/api/v1/ws [send]",
                    response_time=total_time,
                    response_length=0,
                    exception=None,
                    context={}
                )
        except Exception as e:
            events.request.fire(
                request_type="WebSocket",
                name="/api/v1/ws [send]",
                response_time=0,
                response_length=0,
                exception=e,
                context={}
            )
            # Reconnect on error
            self.connect_websocket()


# Performance test configurations
class QuickTest(FastHttpUser):
    """Quick smoke test - 100 users, 1 minute."""
    tasks = [NeuroGraphAPITasks]
    wait_time = between(1, 2)


class LoadTest(FastHttpUser):
    """Standard load test - 500 users, 10 minutes."""
    tasks = [NeuroGraphAPITasks]
    wait_time = between(1, 3)


class StressTest(FastHttpUser):
    """Stress test - 2000+ users, find breaking point."""
    tasks = [NeuroGraphAPITasks]
    wait_time = between(0.5, 2)


class SpikeTest(FastHttpUser):
    """Spike test - rapid user ramp-up."""
    tasks = [NeuroGraphAPITasks]
    wait_time = between(0.1, 1)


if __name__ == "__main__":
    print("""
    NeuroGraph Performance Tests

    Usage:
        # Quick smoke test
        locust -f tests/performance/locustfile.py --host=http://localhost:8000 \\
               --users 100 --spawn-rate 10 --run-time 1m

        # Standard load test
        locust -f tests/performance/locustfile.py --host=http://localhost:8000 \\
               --users 500 --spawn-rate 50 --run-time 10m

        # Stress test
        locust -f tests/performance/locustfile.py --host=http://localhost:8000 \\
               --users 2000 --spawn-rate 100 --run-time 30m

        # WebSocket test
        locust -f tests/performance/locustfile.py --host=http://localhost:8000 \\
               --users 1000 --spawn-rate 50 --run-time 5m \\
               --class-name NeuroGraphWebSocketUser

        # Web UI (default)
        locust -f tests/performance/locustfile.py --host=http://localhost:8000
    """)
