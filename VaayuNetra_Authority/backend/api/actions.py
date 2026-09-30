from typing import List
from fastapi import APIRouter
from backend.models.schemas import ActionCreateRequest, ActionItem
from backend.services.incident_manager import incident_manager

router = APIRouter(tags=["Authority Actions"])


@router.get("/api/v1/actions", response_model=List[ActionItem], summary="List Dispatched Authority Actions")
@router.get("/api/actions", response_model=List[ActionItem], include_in_schema=False)
async def list_actions():
    """Returns all dispatched field actions, notices, and inspections."""
    return incident_manager.get_actions()


@router.post("/api/v1/actions", response_model=ActionItem, summary="Dispatch New Action")
@router.post("/api/actions", response_model=ActionItem, include_in_schema=False)
async def create_action(request: ActionCreateRequest):
    """Dispatches a new authority action (field inspection, stop-work notice, dust suppression)."""
    return incident_manager.create_action(request)
