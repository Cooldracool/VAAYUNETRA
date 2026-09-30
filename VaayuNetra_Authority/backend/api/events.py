from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.models.schemas import (
    ActionCreateRequest,
    ActionItem,
    EnrichedEventItem,
    EventEvidenceResponse,
    EventForecastResponse,
    EventRiskResponse,
)
from backend.services.incident_manager import incident_manager

router = APIRouter(tags=["Authority Events"])


class OutcomeRequest(BaseModel):
    status: str = "RESOLVED"
    verified_source: Optional[str] = "OPEN_BURNING"
    notes: Optional[str] = None
    action_taken: Optional[str] = None


@router.get("/api/v1/events", response_model=List[EnrichedEventItem], summary="List Environmental Events")
@router.get("/api/events", response_model=List[EnrichedEventItem], include_in_schema=False)
async def list_events(
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, CANDIDATE, CORROBORATED, RESOLVED)"),
    severity: Optional[str] = Query(None, description="Filter by severity (critical, high, moderate, low)"),
    city: Optional[str] = Query(None, description="Filter by city/region"),
    pollutant: Optional[str] = Query(None, description="Filter by pollutant parameter (PM2.5, PM10, NO2, SO2, O3)"),
):
    """
    Returns Environmental Events filtered by status, severity, city, or pollutant.
    Powers the Authority Dashboard queue, event detail views, and GIS map layers.
    """
    events = incident_manager.get_enriched_events()
    results = []
    for ev in events:
        if status and ev.status.upper() != status.upper():
            continue
        if severity and ev.severity.lower() != severity.lower():
            continue
        if city and ev.city and city.lower() not in ev.city.lower():
            continue
        if pollutant and ev.pollutant.upper() != pollutant.upper():
            continue
        ev.event_id = ev.id
        results.append(ev)
    return results


@router.get("/api/v1/events/{event_id}", response_model=EnrichedEventItem, summary="Get Environmental Event by ID")
@router.get("/api/events/{event_id}", response_model=EnrichedEventItem, include_in_schema=False)
async def get_event(event_id: str):
    """
    Returns the complete Enriched Environmental Event record including
    evidence lineage, source hypotheses, propagation forecast, and timeline.
    """
    ev = incident_manager.get_enriched_event(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail=f"Environmental Event {event_id} not found")
    ev.event_id = ev.id
    return ev


@router.get("/api/v1/events/{event_id}/evidence", response_model=EventEvidenceResponse, summary="Get Event Evidence (docs/api.md)")
@router.get("/api/events/{event_id}/evidence", response_model=EventEvidenceResponse, include_in_schema=False)
async def get_event_evidence(event_id: str):
    """Returns evidence records and provenance as per docs/api.md."""
    ev = incident_manager.get_enriched_event(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventEvidenceResponse(event_id=ev.id, evidence=ev.evidence)


@router.get("/api/v1/events/{event_id}/forecast", response_model=EventForecastResponse, summary="Get Event Forecast (docs/api.md)")
@router.get("/api/events/{event_id}/forecast", response_model=EventForecastResponse, include_in_schema=False)
async def get_event_forecast(event_id: str):
    """Returns forecast horizons and affected geometries as per docs/api.md."""
    ev = incident_manager.get_enriched_event(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventForecastResponse(event_id=ev.id, forecast=ev.forecast)


@router.get("/api/v1/events/{event_id}/risk", response_model=EventRiskResponse, summary="Get Event Risk & Exposure (docs/api.md)")
@router.get("/api/events/{event_id}/risk", response_model=EventRiskResponse, include_in_schema=False)
async def get_event_risk(event_id: str):
    """Returns exposure and priority components as per docs/api.md."""
    ev = incident_manager.get_enriched_event(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventRiskResponse(event_id=ev.id, priority=ev.priority, exposure=ev.exposure)


@router.post("/api/v1/events/{event_id}/acknowledge", summary="Acknowledge Environmental Event")
@router.post("/api/events/{event_id}/acknowledge", summary="Acknowledge Event (docs/api.md)", include_in_schema=False)
async def acknowledge_event(event_id: str):
    """Marks an environmental event as acknowledged by an on-duty officer."""
    ev = incident_manager.get_enriched_event(event_id)
    inc = incident_manager.get_incident(event_id)
    if not ev and not inc:
        raise HTTPException(status_code=404, detail="Environmental Event not found")
        
    if ev:
        ev.status = "ACTIVE"
        ev.timeline.append({"time": datetime.now(timezone.utc).strftime("%H:%M"), "text": "Event acknowledged by on-duty authority"})
    if inc:
        inc.status = "ACKNOWLEDGED"
        
    return {"status": "success", "event_id": event_id, "current_status": "ACKNOWLEDGED"}


@router.post("/api/v1/events/{event_id}/dispatch", response_model=ActionItem, summary="Dispatch Action for Event")
@router.post("/api/events/{event_id}/dispatch", response_model=ActionItem, include_in_schema=False)
async def dispatch_event_action(event_id: str, action_type: Optional[str] = "FIELD_INSPECTION", assignee: Optional[str] = "SDM South-East"):
    """Dispatches a rapid response action linked to this event."""
    ev = incident_manager.get_enriched_event(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Environmental Event not found")
        
    req = ActionCreateRequest(
        eventId=event_id,
        type=action_type,
        assignee=assignee,
        notes=f"Rapid dispatch for {ev.title}",
    )
    return incident_manager.create_action(req)


@router.post("/api/v1/events/{event_id}/outcome", summary="Record Field Outcome")
@router.post("/api/events/{event_id}/outcome", summary="Record Field Outcome (docs/api.md)", include_in_schema=False)
async def record_event_outcome(event_id: str, outcome: OutcomeRequest):
    """Records field outcome and resolution details for an environmental event."""
    ev = incident_manager.get_enriched_event(event_id)
    inc = incident_manager.get_incident(event_id)
    if not ev and not inc:
        raise HTTPException(status_code=404, detail="Environmental Event not found")
        
    now_time = datetime.now(timezone.utc).strftime("%H:%M")
    if ev:
        ev.status = outcome.status.upper()
        ev.timeline.append({
            "time": now_time,
            "text": f"Incident {outcome.status.upper()}: {outcome.verified_source or ''}. {outcome.notes or ''}",
        })
    if inc:
        inc.status = outcome.status.upper()
        
    return {
        "status": "success",
        "event_id": event_id,
        "current_status": outcome.status.upper(),
        "verified_source": outcome.verified_source,
        "action_taken": outcome.action_taken,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
