from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.config import get_settings
from app.services.reliability import reliability_service

router = APIRouter()
settings = get_settings()


class ReadinessToggleRequest(BaseModel):
    ready: bool = Field(..., description="Desired readiness state")


class LatencyInjectionRequest(BaseModel):
    seconds: float = Field(..., ge=0.0, le=10.0, description="Artificial latency in seconds")


@router.get("/", tags=["Info"])
async def get_application_info():
    """Application metadata endpoint."""
    return {
        "service": settings.app_name,
        "environment": settings.app_env,
        "version": settings.app_version,
        "status": "healthy",
    }


@router.get("/health", tags=["Reliability"])
async def liveness_probe():
    """Process liveness probe."""
    return reliability_service.is_alive()


@router.get("/ready", tags=["Reliability"])
async def readiness_probe():
    """Readiness probe. Returns 503 if service is not ready."""
    status_dict = reliability_service.is_ready()
    if not status_dict.get("ready"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not ready to accept traffic",
        )
    return status_dict


@router.post("/chaos/toggle-readiness", tags=["SRE Chaos Testing"])
async def toggle_readiness(payload: ReadinessToggleRequest):
    """Toggle service readiness to simulate outage or maintenance window."""
    reliability_service.set_readiness(payload.ready)
    return {
        "message": f"Readiness set to {payload.ready}",
        "current_status": reliability_service.is_ready(),
    }


@router.post("/chaos/inject-latency", tags=["SRE Chaos Testing"])
async def inject_latency(payload: LatencyInjectionRequest):
    """Inject artificial request latency to test SLO degradation and alerts."""
    reliability_service.set_latency_simulation(payload.seconds)
    return {"message": f"Artificial latency set to {payload.seconds}s"}


@router.get("/chaos/error", tags=["SRE Chaos Testing"])
async def simulate_internal_error():
    """Deliberately raises an HTTP 500 error to test Prometheus alert firing."""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Simulated internal server error for Prometheus alerting test",
    )
