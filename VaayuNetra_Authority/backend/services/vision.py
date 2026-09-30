import io
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import numpy as np

from backend.config import UPLOADS_DIR
from backend.models.schemas import AIVisionResult
from backend.services.gemini_service import analyze_image_with_gemini


async def process_incident_image(
    file_bytes: bytes,
    filename: str,
    reported_category: Optional[str] = None,
) -> Tuple[AIVisionResult, str]:
    """
    Validates citizen uploaded photo, saves it, and runs Google Gemini Multimodal Vision analysis
    to detect smoke, open burning, stubble fires, dust, or industrial plume signatures.
    
    Returns (AIVisionResult, saved_file_path).
    """
    ext = Path(filename).suffix.lower() if filename else ".jpg"
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"
        
    saved_filename = f"{uuid.uuid4().hex[:12]}{ext}"
    saved_filepath = UPLOADS_DIR / saved_filename
    
    # Save image to storage
    with open(saved_filepath, "wb") as f:
        f.write(file_bytes)
        
    # Analyze with Google Gemini Multimodal Vision
    result = await analyze_image_with_gemini(
        file_bytes=file_bytes,
        filename=filename,
        reported_category=reported_category,
    )
        
    return result, str(saved_filepath)
