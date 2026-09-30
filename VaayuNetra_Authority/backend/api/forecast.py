from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from backend.models.schemas import HourlyForecastResponse, RegionInfo
from backend.services.incident_manager import incident_manager

router = APIRouter(tags=["Air Quality Forecasting"])


@router.get("/api/v1/forecast/regions", response_model=List[RegionInfo], summary="Supported Indian Regions Catalog")
@router.get("/api/forecast/regions", response_model=List[RegionInfo], include_in_schema=False)
async def list_regions():
    """Returns the catalog of 10 major Indian regions with coordinates and baseline conditions."""
    return incident_manager.get_regions()


@router.get("/api/v1/forecast/hourly", response_model=HourlyForecastResponse, summary="Regional Hourly Forecast")
@router.get("/api/forecast/hourly", response_model=HourlyForecastResponse, include_in_schema=False)
async def get_hourly_forecast(
    city: Optional[str] = Query("Delhi NCR", description="City name (e.g., Mumbai, Bengaluru, Kolkata, Delhi NCR, Chennai, Hyderabad, Ahmedabad, Pune, Lucknow, Patna, Ranchi)"),
    region: Optional[str] = Query(None, description="Region alias"),
):
    """
    Returns the 24-hour diurnal air quality trajectory and current AQI status
    for any supported Indian metropolitan region.
    """
    target_city = region or city or "Delhi NCR"
    return incident_manager.get_regional_forecast(target_city)


@router.get("/api/v1/forecast/events", response_model=List[Dict[str, Any]], summary="Active Event Propagation Forecasts")
@router.get("/api/forecast/events", response_model=List[Dict[str, Any]], include_in_schema=False)
async def get_event_propagation_forecasts():
    """Returns active event propagation horizons (+1h, +3h, +6h) across regions."""
    events = incident_manager.get_enriched_events()
    results = []
    for ev in events:
        if ev.forecast:
            results.append({
                "eventId": ev.id,
                "title": ev.title,
                "city": ev.city or "Delhi NCR",
                "forecast": ev.forecast,
            })
    return results
