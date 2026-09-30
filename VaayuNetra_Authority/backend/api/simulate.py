from fastapi import APIRouter
from backend.models.schemas import AIVisionResult, IncidentTicketResponse, SimulateSpikeRequest
from backend.services.incident_manager import incident_manager

router = APIRouter(prefix="/api/v1/simulate", tags=["Pitch & Demo Simulations"])


@router.post("/spike", response_model=IncidentTicketResponse, summary="Simulate Pollution Spike or Fire")
async def simulate_spike(request: SimulateSpikeRequest):
    """
    Demo triggers and pitch simulations without needing a fresh camera photo.
    Creates an immediate active incident with simulated AI vision confidence,
    satellite thermal anomaly match, calculated downwind dispersion plume,
    and vulnerable receptor impact analysis.
    """
    # Simulate high-confidence vision detection
    category_label = request.category.upper() if request.category else "OPEN_BURNING"
    simulated_vision = AIVisionResult(
        confidence=0.94,
        detected_category=category_label,
        visual_evidence=True,
        model_version="VaayuNetra-Vision-v1.0 (Simulation Engine)",
        details=f"Live simulation trigger: Synthetic high-contrast plume signature generated for {request.category}.",
    )
    
    ticket = await incident_manager.create_incident_ticket(
        latitude=request.latitude or 28.6139,
        longitude=request.longitude or 77.2090,
        category=request.category or "waste_burning",
        ai_vision=simulated_vision,
        custom_wind_speed=request.wind_speed_mps,
        custom_wind_deg=request.wind_direction_deg,
        custom_severity=request.severity or "HIGH",
    )
    
    return ticket
