from typing import List
from fastapi import APIRouter, HTTPException
from backend.models.schemas import AdvisoryCreateRequest, AdvisoryItem
from backend.services.incident_manager import incident_manager

router = APIRouter(tags=["Public Advisories"])


@router.get("/api/v1/advisories", response_model=List[AdvisoryItem], summary="List Public Health Advisories")
@router.get("/api/advisories", response_model=List[AdvisoryItem], include_in_schema=False)
async def list_advisories():
    """Returns all public health advisories across SMS, IVR, and mobile apps."""
    return incident_manager.get_advisories()


@router.post("/api/v1/advisories", response_model=AdvisoryItem, summary="Compose & Broadcast Advisory")
@router.post("/api/advisories", response_model=AdvisoryItem, include_in_schema=False)
async def create_advisory(request: AdvisoryCreateRequest):
    """Composes and broadcasts an advisory to the target demographic."""
    return incident_manager.create_advisory(request)


@router.post("/api/v1/advisories/{advisory_id}/send", response_model=AdvisoryItem, summary="Send Draft Advisory")
@router.post("/api/advisories/{advisory_id}/send", response_model=AdvisoryItem, include_in_schema=False)
async def send_advisory(advisory_id: str):
    """Sends a previously drafted advisory."""
    adv = incident_manager.send_advisory(advisory_id)
    if not adv:
        raise HTTPException(status_code=404, detail="Advisory not found")
    return adv
