from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from backend.models.schemas import IncidentTicketResponse
from backend.services.incident_manager import incident_manager
from backend.services.vision import process_incident_image

router = APIRouter(tags=["Incident Reporting"])


@router.post("/api/v1/report", response_model=IncidentTicketResponse, summary="Submit Citizen Incident Report")
@router.post("/api/citizen-reports", response_model=IncidentTicketResponse, summary="Submit Citizen Report (docs/api.md)", include_in_schema=False)
@router.post("/api/v1/citizen-reports", response_model=IncidentTicketResponse, include_in_schema=False)
async def report_incident(
    latitude: float = Form(..., description="Latitude of the observation"),
    longitude: float = Form(..., description="Longitude of the observation"),
    category: str = Form("waste_burning", description="Reported category, e.g., waste_burning, industrial_emission"),
    file: UploadFile = File(..., description="Image upload showing smoke, fire, or pollution source"),
):
    """
    Incident reporting screen endpoint.
    Accepts multipart form-data (latitude, longitude, category, file).
    
    Processes the image using server-side AI computer vision, queries NASA FIRMS satellite
    thermal hotspots, calculates the downwind Gaussian dispersion plume polygon, and intersects
    the plume with vulnerable sensitive receptors (schools/hospitals).
    
    Returns a unified IncidentTicketResponse.
    """
    if not file:
        raise HTTPException(status_code=400, detail="Image file is required for visual evidence validation.")
        
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
    # 1. AI Vision Inference
    ai_vision, saved_path = await process_incident_image(
        file_bytes=contents,
        filename=file.filename or "report.jpg",
        reported_category=category,
    )
    
    # 2. Generate unified Incident Ticket with all evidence fusion
    ticket = await incident_manager.create_incident_ticket(
        latitude=latitude,
        longitude=longitude,
        category=category,
        ai_vision=ai_vision,
    )
    
    return ticket
