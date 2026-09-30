"""Vision Model: Local YOLO and Dynamic Pixel Analysis for Fire and Smoke Verification.

Integrates Ultralytics YOLOv8n with photometric analysis to accurately classify
and verify photographic evidence of biomass burning, stubble burning, and smoke plumes.
"""

from typing import Any, Dict, List, Optional
import asyncio
import io
import logging
import os
import numpy as np
from PIL import Image
from ultralytics import YOLO

logger = logging.getLogger("vaayunetra.vision")

# Globally cached YOLO model instance
_YOLO_MODEL: Optional[YOLO] = None

# Semantic keywords for smoke, fire, and outdoor combustion detection
SMOKE_FIRE_KEYWORDS = {
    "smoke", "fire", "flame", "blaze", "burn", "haze", "smog", "pollution"
}
COMBUSTION_OUTDOOR_KEYWORDS = {
    "truck", "car", "bus", "train", "boat", "airplane", "traffic light",
    "fire hydrant", "motorcycle", "chimney"
}


def get_yolo_model() -> YOLO:
    """Retrieve or lazily initialize the singleton YOLO model from disk."""
    global _YOLO_MODEL
    if _YOLO_MODEL is None:
        weights_name = "yolov8n.pt"
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        weights_path = os.path.join(base_dir, weights_name)
        if not os.path.exists(weights_path):
            weights_path = weights_name

        logger.info("Loading YOLO weights from: %s", weights_path)
        _YOLO_MODEL = YOLO(weights_path)
        # Warm up model with a dummy 64x64 frame for instant subsequent inference
        try:
            dummy_img = Image.new("RGB", (64, 64), (128, 128, 128))
            _YOLO_MODEL(dummy_img, verbose=False)
            logger.info("YOLOv8n model initialized and warmed up successfully.")
        except Exception as e:
            logger.warning("Warmup inference failed: %s", e)

    return _YOLO_MODEL


def init_yolo_model() -> None:
    """Explicitly pre-load the YOLO model into memory during server startup."""
    get_yolo_model()


def _analyze_smoke_pixels(rgb_img: Image.Image) -> Dict[str, float]:
    """Calculate photometric luminance, contrast, and gray/brown smoke pixel distribution."""
    # Downsample to 128x128 for rapid sub-millisecond pixel distribution analysis
    small_img = rgb_img.resize((128, 128), Image.Resampling.BILINEAR)
    img_array = np.array(small_img, dtype=np.float32)

    r = img_array[:, :, 0]
    g = img_array[:, :, 1]
    b = img_array[:, :, 2]

    # Standard photometric luminance: 0.299*R + 0.587*G + 0.114*B
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    brightness = float(np.mean(luminance))
    contrast = float(np.std(luminance))

    rg_diff = np.abs(r - g)
    gb_diff = np.abs(g - b)
    rb_diff = np.abs(r - b)

    # 1. Grayish/white smoke condition (low saturation, moderate/high brightness)
    gray_smoke = (
        (rg_diff < 28.0)
        & (gb_diff < 28.0)
        & (rb_diff < 32.0)
        & (luminance >= 65.0)
        & (luminance <= 245.0)
    )

    # 2. Brownish/yellowish biomass burning smoke (red & green exceed blue)
    brown_smoke = (
        (r > b + 14.0)
        & (g > b + 4.0)
        & (r >= 70.0)
        & (r <= 235.0)
        & (b <= 165.0)
    )

    # 3. Dense dark soot plume
    dark_soot = (
        (rg_diff < 20.0)
        & (gb_diff < 20.0)
        & (luminance >= 20.0)
        & (luminance < 65.0)
    )

    smoke_pixels = gray_smoke | brown_smoke | dark_soot
    smoke_ratio = float(np.sum(smoke_pixels) / (128 * 128))

    return {
        "brightness": round(brightness, 1),
        "contrast": round(contrast, 1),
        "smoke_pixel_ratio": round(smoke_ratio, 3),
    }


def _verify_pollution_image_sync(image_bytes: bytes) -> Dict[str, Any]:
    """Synchronous core vision verification executing YOLO and pixel analysis."""
    if not image_bytes or len(image_bytes) == 0:
        return {
            "verified": False,
            "confidence": 0.0,
            "detected_classes": [],
            "label": "No Evidence Provided",
            "error": "Image payload is empty or invalid.",
        }

    # Format inspection
    detected_format = "unknown"
    if image_bytes.startswith(b"\xff\xd8\xff"):
        detected_format = "jpeg"
    elif image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        detected_format = "png"
    elif image_bytes.startswith(b"RIFF") and b"WEBP" in image_bytes[:16]:
        detected_format = "webp"

    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            rgb_img = img.convert("RGB")
    except Exception:
        # Fallback for synthetic unformatted test payloads
        logger.warning("Uploaded byte stream could not be decoded by PIL.")
        return {
            "verified": False,
            "confidence": 0.15,
            "detected_classes": [],
            "label": "Corrupted or Invalid Image Format",
            "error": "Failed to decode image.",
        }

    # Step 1: Run local YOLO inference
    model = get_yolo_model()
    yolo_results = model(rgb_img, verbose=False)

    detected_classes: List[str] = []
    max_yolo_conf = 0.0
    direct_fire_smoke = False
    combustion_indicator = False

    if yolo_results and len(yolo_results) > 0 and yolo_results[0].boxes is not None:
        for box in yolo_results[0].boxes:
            cls_id = int(box.cls[0].item())
            cls_name = model.names.get(cls_id, str(cls_id)).lower()
            conf = float(box.conf[0].item())
            if cls_name not in detected_classes:
                detected_classes.append(cls_name)
            if conf > max_yolo_conf:
                max_yolo_conf = conf

            if any(k in cls_name for k in SMOKE_FIRE_KEYWORDS):
                direct_fire_smoke = True
            elif any(k in cls_name for k in COMBUSTION_OUTDOOR_KEYWORDS):
                combustion_indicator = True

    # Step 2: Run dynamic photometric smoke distribution analysis
    pixel_metrics = _analyze_smoke_pixels(rgb_img)
    smoke_ratio = pixel_metrics["smoke_pixel_ratio"]
    contrast = pixel_metrics["contrast"]
    brightness = pixel_metrics["brightness"]

    # Step 3: Compute verification confidence & classification
    # Case A: Direct YOLO fire/smoke class detection
    if direct_fire_smoke:
        confidence = round(max(0.85, max_yolo_conf), 2)
        verified = True
        label = "Active Fire / Smoke Verified by YOLO"

    # Case B: Combustion indicators (traffic, transport, industrial) with smoke/haze present
    elif combustion_indicator and smoke_ratio >= 0.15:
        confidence = round(min(0.96, 0.60 + 0.25 * smoke_ratio + 0.15 * max_yolo_conf), 2)
        verified = True
        label = "Combustion Emissions & Smoke Plume Verified"

    # Case C: Prominent visual smoke / biomass burning plume distribution
    elif smoke_ratio >= 0.25:
        if "biomass_smoke" not in detected_classes:
            detected_classes.append("biomass_smoke")
        contrast_factor = min(0.06, contrast / 500.0)
        calc_conf = 0.65 + (smoke_ratio * 0.25) + contrast_factor
        confidence = round(min(0.95, max(0.68, calc_conf)), 2)
        verified = True
        label = "Dense Biomass Burning Smoke Plume Verified"

    # Case D: Weak detection or low-density haze
    elif combustion_indicator and smoke_ratio < 0.15:
        confidence = round(min(0.72, 0.45 + 0.25 * max_yolo_conf), 2)
        verified = True
        label = "Outdoor Combustion Source Detected"

    # Case E: Edge case - No object and no smoke detected
    else:
        # Verified is False when no smoke or relevant combustion source is observed
        verified = False
        confidence = round(max(0.08, min(0.35, smoke_ratio * 0.8)), 2)
        label = "No Smoke or Fire Detected"

    return {
        "verified": verified,
        "confidence": confidence,
        "detected_classes": detected_classes,
        "label": label,
        "format": detected_format,
        "byte_size": len(image_bytes),
        "brightness": brightness,
        "contrast": contrast,
        "smoke_pixel_ratio": smoke_ratio,
    }


async def verify_pollution_image(image_bytes: bytes) -> Dict[str, Any]:
    """Async inference helper that runs YOLO in a background thread for non-blocking execution.

    Args:
        image_bytes: Raw bytes of uploaded photographic evidence.

    Returns:
        Verification dictionary containing verified status, confidence, detected_classes, and label.
    """
    return await asyncio.to_thread(_verify_pollution_image_sync, image_bytes)


def verify_image_evidence(image_bytes: bytes) -> Dict[str, Any]:
    """Synchronous backward-compatible wrapper for vision verification."""
    return _verify_pollution_image_sync(image_bytes)
