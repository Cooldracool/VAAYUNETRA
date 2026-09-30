from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="VaayuNetra Telemetry Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.feed import get_telemetry_feed, router as feed_router

app.include_router(feed_router)

@app.post("/api/v1/report")
async def report_incident(file: UploadFile = File(None)):
    return {
        "success": True,
        "ticket_id": "TKT-8924",
        "verification": {
            "vision_verified": True,
            "confidence": 0.88,
            "label": "Confirmed Biomass / Smoke Signature",
            "source_type": "open_combustion"
        },
        "plume_forecast": {
            "dispersion_radius_m": 850,
            "wind_trajectory": "NE",
            "threatened_receptors": ["City General Hospital", "DAV Public School"]
        }
    }

@app.get("/api/v1/alerts/check")
def check_alerts(lat: float = 25.5941, lon: float = 85.1376):
    return {
        "inside_hazard_zone": True,
        "hazard_type": "smoke_plume_dispersion",
        "distance_km": 1.2,
        "severity": "high",
        "message": "Hazard Zone: You are inside the downwind smoke dispersion path (~1.2 km from reported fire)."
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

