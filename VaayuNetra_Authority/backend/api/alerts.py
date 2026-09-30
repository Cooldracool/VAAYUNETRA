from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from backend.models.schemas import AlertItem, EnrichedEventItem, SensorDataInput
from backend.services.incident_manager import incident_manager

router = APIRouter(tags=["Alerts & Sensor Ingestion"])


@router.get("/api/v1/alerts", response_model=List[AlertItem], summary="List Operational Alerts")
@router.get("/api/alerts", response_model=List[AlertItem], include_in_schema=False)
async def list_alerts():
    """Returns alerts visible to the authenticated authority as per docs/api.md."""
    return incident_manager.get_alerts()


@router.post("/api/v1/alerts/{alert_id}/acknowledge", response_model=AlertItem, summary="Acknowledge Alert")
@router.post("/api/alerts/{alert_id}/acknowledge", response_model=AlertItem, include_in_schema=False)
async def acknowledge_alert(alert_id: str):
    """Marks an alert as acknowledged."""
    alt = incident_manager.acknowledge_alert(alert_id)
    if not alt:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alt


@router.get("/api/v1/corridors/{corridor_id}/events", response_model=List[EnrichedEventItem], summary="Get Corridor Events")
@router.get("/api/corridors/{corridor_id}/events", response_model=List[EnrichedEventItem], include_in_schema=False)
async def get_corridor_events(corridor_id: str):
    """Returns active/recent events intersecting the specified corridor as per docs/api.md."""
    return incident_manager.get_corridor_events(corridor_id)


@router.post("/api/v1/sensor-data", summary="Ingest Normalized Sensor Data")
@router.post("/api/sensor-data", summary="Ingest Normalized Sensor Data (docs/api.md)", include_in_schema=False)
async def ingest_sensor_data(data: SensorDataInput):
    """Ingests normalized sensor data observation conforming to docs/api.md contract."""
    return incident_manager.record_sensor_data(data)
