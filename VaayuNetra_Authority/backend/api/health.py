from datetime import datetime, timezone
from fastapi import APIRouter
from backend.config import APP_NAME, APP_VERSION
from backend.models.schemas import HealthResponse
from backend.services.incident_manager import incident_manager

router = APIRouter(tags=["Health"])


@router.get("/", response_model=HealthResponse, summary="System Health & API Discovery")
async def health_check():
    """
    System health check to confirm server connectivity and discover primary BFF endpoints.
    """
    return HealthResponse(
        status="healthy",
        service=APP_NAME,
        version=APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        endpoints={
            "feed": "/api/v1/feed?lat={lat}&lon={lon}",
            "report": "/api/v1/report",
            "municipal_incidents": "/api/v1/municipal/incidents",
            "simulate_spike": "/api/v1/simulate/spike",
            "events": "/api/v1/events",
            "docs": "/docs",
        },
        active_incidents_count=len(incident_manager.get_all_incidents()),
    )
