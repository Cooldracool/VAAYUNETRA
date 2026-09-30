from fastapi import APIRouter
from backend.models.schemas import GeoJSONFeatureCollection
from backend.services.incident_manager import incident_manager

router = APIRouter(prefix="/api/v1/municipal", tags=["Municipal Operations"])


@router.get("/incidents", response_model=GeoJSONFeatureCollection, summary="Municipal Incidents Map Feed")
async def get_municipal_incidents():
    """
    Map dashboard endpoint (Web & Mobile).
    Returns a standard GeoJSON FeatureCollection containing all verified incident points
    and their projected downwind plume dispersion polygons ready to render directly on Leaflet / Mapbox.
    """
    return incident_manager.get_municipal_geojson()
