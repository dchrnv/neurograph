"""
Health Check Endpoints (v0.67.0)

Comprehensive health checks for monitoring and Kubernetes probes:
- /health - Basic health check with component details
- /health/live - Liveness probe (is process running?)
- /health/ready - Readiness probe (can handle traffic?)
- /health/startup - Startup probe (has app started?)
- /health/components - Detailed component status

Kubernetes probe support:
- livenessProbe: /health/live
- readinessProbe: /health/ready
- startupProbe: /health/startup

Version: v0.67.0
"""

from fastapi import APIRouter, Depends, Response, status
from ..models.response import ApiResponse
from ..models.status import HealthResponse, ReadinessResponse
from ..dependencies import get_runtime, get_token_storage, get_grid_storage, get_cdna_storage
from ..logging_config import get_logger
from ..websocket.manager import connection_manager
from typing import Dict, Any
import time
import psutil
import os

router = APIRouter()
logger = get_logger(__name__, component="health")

# Application lifecycle state
_start_time = time.time()
_startup_complete = False
_min_startup_time = 2.0  # Minimum time before ready (allow components to initialize)
_process = psutil.Process(os.getpid())


def _get_system_metrics() -> Dict[str, Any]:
    """
    Get current system resource metrics.

    Returns:
        Dictionary with CPU, memory, and disk metrics
    """
    try:
        cpu_percent = _process.cpu_percent(interval=0.1)
        memory_info = _process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        memory_percent = _process.memory_percent()

        return {
            "cpu_percent": round(cpu_percent, 2),
            "memory_mb": round(memory_mb, 2),
            "memory_percent": round(memory_percent, 2),
            "threads": _process.num_threads()
        }
    except Exception as e:
        logger.warning(f"Failed to get system metrics: {e}")
        return {
            "cpu_percent": 0.0,
            "memory_mb": 0.0,
            "memory_percent": 0.0,
            "threads": 0
        }


def _check_component_health(
    runtime,
    token_storage,
    grid_storage,
    cdna_storage
) -> Dict[str, Dict[str, Any]]:
    """
    Check health of all system components.

    Returns:
        Dictionary with component health status and metrics
    """
    components = {}

    # Check Runtime Core
    try:
        runtime_ok = runtime is not None
        components["rust_core"] = {
            "status": "healthy" if runtime_ok else "unavailable",
            "message": "Rust FFI initialized" if runtime_ok else "Runtime not initialized"
        }
    except Exception as e:
        components["rust_core"] = {
            "status": "error",
            "message": str(e)
        }

    # Check Token Storage
    try:
        token_count = token_storage.count()
        components["token_storage"] = {
            "status": "healthy",
            "token_count": token_count,
            "backend": "runtime" if runtime is not None else "memory"
        }
    except Exception as e:
        components["token_storage"] = {
            "status": "error",
            "message": str(e)
        }

    # Check Grid Storage
    try:
        grid_info = grid_storage.get_grid(0)
        components["grid_storage"] = {
            "status": "healthy" if grid_info is not None else "initializing",
            "message": "Grid operational" if grid_info else "Default grid not found"
        }
    except Exception as e:
        components["grid_storage"] = {
            "status": "error",
            "message": str(e)
        }

    # Check CDNA Storage
    try:
        cdna_count = len(cdna_storage.list_profiles())
        components["cdna_storage"] = {
            "status": "healthy",
            "profile_count": cdna_count
        }
    except Exception as e:
        components["cdna_storage"] = {
            "status": "error",
            "message": str(e)
        }

    # Check WebSocket Manager
    try:
        ws_stats = connection_manager.get_connection_stats()
        components["websocket"] = {
            "status": "healthy",
            "active_connections": ws_stats["total_connections"],
            "total_channels": ws_stats["total_channels"],
            "total_subscriptions": ws_stats["total_subscriptions"],
            "buffered_events": ws_stats["buffered_events"]
        }
    except Exception as e:
        components["websocket"] = {
            "status": "error",
            "message": str(e)
        }

    return components


@router.get("/health", response_model=ApiResponse)
async def health_check(
    runtime=Depends(get_runtime),
    token_storage=Depends(get_token_storage),
    grid_storage=Depends(get_grid_storage),
    cdna_storage=Depends(get_cdna_storage)
):
    """
    Enhanced health check endpoint (v0.67.0).

    Returns overall health status with detailed component information,
    system metrics, and uptime. For Kubernetes, use specific probes:
    /health/live, /health/ready, or /health/startup.

    Response:
        - status: "healthy" | "degraded" | "unhealthy"
        - uptime_seconds: time since startup
        - version: API version
        - components: detailed status of all components
        - system: CPU, memory, and thread metrics
    """
    uptime = time.time() - _start_time

    # Get component health
    components = _check_component_health(runtime, token_storage, grid_storage, cdna_storage)

    # Get system metrics
    system_metrics = _get_system_metrics()

    # Determine overall health status
    error_count = sum(1 for c in components.values() if c["status"] == "error")
    unavailable_count = sum(1 for c in components.values() if c["status"] == "unavailable")

    if error_count > 0:
        health_status = "unhealthy"
    elif unavailable_count > 0:
        health_status = "degraded"
    else:
        health_status = "healthy"

    data = HealthResponse(
        status=health_status,
        uptime_seconds=uptime,
        version="0.67.0"
    )
    response_data = data.dict()
    response_data["components"] = components
    response_data["system"] = system_metrics

    return ApiResponse.success_response(response_data)


@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe for Kubernetes (v0.52.0).

    Answers: "Is the application process alive?"

    Returns 200 if the process is running.
    Returns 503 only if the application is critically broken.

    This is a lightweight check - if this fails, Kubernetes will restart the pod.
    Use for: livenessProbe in Kubernetes deployment

    Response Codes:
        200: Process is alive and running
        503: Process is critically broken (rare)
    """
    # This is intentionally minimal - just check that Python is executing
    return {"status": "alive", "check": "liveness"}


@router.get("/health/components", response_model=ApiResponse)
async def components_check(
    runtime=Depends(get_runtime),
    token_storage=Depends(get_token_storage),
    grid_storage=Depends(get_grid_storage),
    cdna_storage=Depends(get_cdna_storage)
):
    """
    Detailed component health check (v0.67.0).

    Returns detailed status and metrics for each system component.
    Useful for debugging and monitoring dashboards.

    Response:
        - components: detailed status of all components
        - system: CPU, memory, and thread metrics
        - uptime_seconds: time since startup
    """
    uptime = time.time() - _start_time

    # Get component health
    components = _check_component_health(runtime, token_storage, grid_storage, cdna_storage)

    # Get system metrics
    system_metrics = _get_system_metrics()

    response_data = {
        "components": components,
        "system": system_metrics,
        "uptime_seconds": round(uptime, 2)
    }

    return ApiResponse.success_response(response_data)


@router.get("/health/ready", response_model=ApiResponse)
async def readiness_check(
    runtime=Depends(get_runtime),
    token_storage=Depends(get_token_storage),
    grid_storage=Depends(get_grid_storage)
):
    """
    Readiness probe for Kubernetes (v0.67.0).

    Answers: "Can the application handle traffic?"

    Checks:
    - Runtime initialized
    - Token storage operational
    - Grid storage accessible
    - Minimum uptime elapsed (avoid thundering herd)

    Returns 200 if ready to serve traffic, 503 if not ready.
    Use for: readinessProbe in Kubernetes deployment

    Response Codes:
        200: Ready to handle traffic
        503: Not ready (temporarily unavailable)
    """
    global _startup_complete

    checks = {}
    uptime = time.time() - _start_time

    # Check minimum uptime (avoid marking ready too quickly)
    if uptime < _min_startup_time and not _startup_complete:
        logger.debug("Readiness check: still starting up")
        return Response(
            content='{"ready": false, "reason": "startup_in_progress"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )

    # Check runtime
    try:
        runtime_ready = runtime is not None
        checks["runtime"] = "ok" if runtime_ready else "not_initialized"
    except Exception as e:
        logger.warning(f"Runtime check failed: {e}")
        checks["runtime"] = "error"

    # Check token storage
    try:
        _ = token_storage.count()  # Quick operation test
        checks["token_storage"] = "ok"  # noqa: B105 - Status string, not a password
    except Exception as e:
        logger.warning(f"Token storage check failed: {e}")
        checks["token_storage"] = "error"  # noqa: B105 - Status string, not a password

    # Check grid storage
    try:
        grid_info = grid_storage.get_grid(0)
        checks["grid_storage"] = "ok" if grid_info is not None else "not_ready"
    except Exception as e:
        logger.warning(f"Grid storage check failed: {e}")
        checks["grid_storage"] = "error"

    ready = all(check_status == "ok" for check_status in checks.values())

    if ready:
        _startup_complete = True  # Mark startup as complete
        data = ReadinessResponse(ready=True, checks=checks)
        return ApiResponse.success_response(data.dict())
    else:
        logger.warning(f"Readiness check failed: {checks}")
        return Response(
            content=f'{{"ready": false, "checks": {checks}}}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )


@router.get("/health/startup")
async def startup_check(
    runtime=Depends(get_runtime),
    token_storage=Depends(get_token_storage)
):
    """
    Startup probe for Kubernetes (v0.52.0).

    Answers: "Has the application completed its startup sequence?"

    This probe indicates when the application has finished initializing
    and is ready for liveness/readiness probes to begin.

    Returns 200 once startup is complete, 503 while starting.
    Use for: startupProbe in Kubernetes deployment (optional)

    Response Codes:
        200: Startup complete
        503: Still starting up

    Startup Criteria:
    - Runtime initialized
    - Token storage accessible
    - Minimum uptime elapsed (allow Rust FFI to initialize)
    """
    global _startup_complete

    uptime = time.time() - _start_time

    # Quick startup checks
    try:
        # Check runtime and basic storage
        runtime_ok = runtime is not None
        storage_ok = token_storage.count() >= 0  # Just check it doesn't error

        # Check minimum uptime
        uptime_ok = uptime >= _min_startup_time

        startup_complete = runtime_ok and storage_ok and uptime_ok

        if startup_complete:
            _startup_complete = True
            return {
                "started": True,
                "uptime_seconds": round(uptime, 2),
                "checks": {
                    "runtime": "ok",
                    "storage": "ok",
                    "uptime": "ok"
                }
            }
        else:
            return Response(
                content='{"started": false, "reason": "initialization_in_progress"}',
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                media_type="application/json"
            )

    except Exception as e:
        logger.error(f"Startup check failed: {e}")
        return Response(
            content=f'{{"started": false, "error": "{str(e)}"}}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )
