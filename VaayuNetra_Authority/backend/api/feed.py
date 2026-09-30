from fastapi import APIRouter, Query
from backend.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE
from backend.models.schemas import FeedResponse
from backend.services.incident_manager import incident_manager
from backend.services.sensors import get_health_recommendations, get_nearby_sensors
from backend.services.weather import get_feed_weather

router = APIRouter(prefix="/api/v1", tags=["Citizen Feed"])


@router.get("/feed", response_model=FeedResponse, summary="Citizen Home Radar")
async def get_citizen_feed(
    lat: float = Query(DEFAULT_LATITUDE, description="User latitude (e.g., 28.6139)"),
    lon: float = Query(DEFAULT_LONGITUDE, description="User longitude (e.g., 77.2090)"),
):
    """
    Citizen Home Radar endpoint.
    Returns:
    - Street-level PM2.5 readings calculated from nearby sensors
    - Active warnings array flagging if the user is inside an active smoke plume
    - Local meteorology (wind speed, wind direction, temp, humidity)
    - Actionable health recommendations
    """
    # 1. Check if user is inside any active smoke plume
    active_warnings = incident_manager.check_active_warnings(lat, lon)
    is_inside_plume = any(w.inside_plume for w in active_warnings)
    
    # 2. Get nearby sensors and IDW interpolated street-level PM2.5
    current_pm25, aqi, aqi_category, nearby_sensors = get_nearby_sensors(lat, lon)
    
    # If inside plume, elevate PM2.5 exposure reading
    if is_inside_plume:
        current_pm25 = round(current_pm25 + 95.0, 1)
        aqi = min(500, aqi + 75)
        aqi_category = "Severe" if aqi >= 401 else "Very Poor"
        
    # 3. Fetch local meteorological context
    weather = await get_feed_weather(lat, lon)
    
    # 4. Tailor health recommendations
    recommendations = get_health_recommendations(aqi, is_inside_plume)
    
    return FeedResponse(
        latitude=lat,
        longitude=lon,
        current_pm25=current_pm25,
        aqi=aqi,
        aqi_category=aqi_category,
        dominant_pollutant="PM2.5",
        nearby_sensors=nearby_sensors,
        active_warnings=active_warnings,
        weather=weather,
        recommendations=recommendations,
    )
