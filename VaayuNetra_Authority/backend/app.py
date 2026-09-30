from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.actions import router as actions_router
from backend.api.advisories import router as advisories_router
from backend.api.alerts import router as alerts_router
from backend.api.events import router as events_router
from backend.api.feed import router as feed_router
from backend.api.forecast import router as forecast_router
from backend.api.health import router as health_router
from backend.api.municipal import router as municipal_router
from backend.api.notices import router as notices_router
from backend.api.report import router as report_router
from backend.api.simulate import router as simulate_router
from backend.config import APP_NAME, APP_VERSION, BASE_DIR, CORS_ORIGINS, UPLOADS_DIR

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Central FastAPI Backend-For-Frontend (BFF) for VaayuNetra. "
        "Handles server-side parallel fetching, AI vision evidence analysis, "
        "NASA FIRMS satellite thermal correlation, Open-Meteo wind vector retrieval, "
        "atmospheric Gaussian plume dispersion modeling, multi-region Indian forecasting, "
        "and sensitive receptor intersection."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for Web Dashboard, Android Emulator, and Localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include BFF and API Routers
app.include_router(health_router)
app.include_router(feed_router)
app.include_router(report_router)
app.include_router(municipal_router)
app.include_router(simulate_router)
app.include_router(events_router)
app.include_router(actions_router)
app.include_router(advisories_router)
app.include_router(forecast_router)
app.include_router(notices_router)
app.include_router(alerts_router)

# Mount uploads directory for photo evidence
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Mount frontend assets if directory exists
css_dir = BASE_DIR / "css"
js_dir = BASE_DIR / "js"
if css_dir.exists():
    app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
if js_dir.exists():
    app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")


@app.get("/dashboard", include_in_schema=False)
async def serve_dashboard():
    """Serves the Authority Web Dashboard."""
    index_file = BASE_DIR / "index.html"
    if not index_file.exists():
        index_file = BASE_DIR / "index.hmtl"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Authority Dashboard index.html not found"}
