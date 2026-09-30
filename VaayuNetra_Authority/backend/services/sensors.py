from datetime import datetime, timezone
import math
from typing import Dict, List, Tuple
from backend.models.schemas import NearbySensor
from backend.services.dispersion import calculate_distance_meters

# Real CAAQMS and hyper-local IoT monitoring stations in Delhi-NCR
CAAQMS_STATIONS = [
    {"id": "DEL-AQ-01", "name": "Anand Vihar CAAQMS", "lat": 28.6476, "lon": 77.3158, "base_pm25": 168.0},
    {"id": "DEL-AQ-02", "name": "RK Puram Sector 5 CAAQMS", "lat": 28.5633, "lon": 77.1869, "base_pm25": 112.0},
    {"id": "DEL-AQ-03", "name": "Punjabi Bagh CAAQMS", "lat": 28.6741, "lon": 77.1310, "base_pm25": 134.0},
    {"id": "DEL-AQ-04", "name": "Mandir Marg Station", "lat": 28.6365, "lon": 77.2010, "base_pm25": 94.0},
    {"id": "DEL-AQ-05", "name": "IGI Airport T3 Ambient", "lat": 28.5562, "lon": 77.0999, "base_pm25": 88.0},
    {"id": "DEL-AQ-06", "name": "Bawana Industrial IoT Grid", "lat": 28.7990, "lon": 77.0320, "base_pm25": 195.0},
    {"id": "DEL-AQ-07", "name": "Okhla Phase II Station", "lat": 28.5310, "lon": 77.2710, "base_pm25": 142.0},
    {"id": "DEL-AQ-08", "name": "Dwarka Sector 8 CAAQMS", "lat": 28.5710, "lon": 77.0710, "base_pm25": 105.0},
    {"id": "DEL-AQ-09", "name": "Rohini Sector 16 IoT Node", "lat": 28.7320, "lon": 77.1190, "base_pm25": 128.0},
    {"id": "DEL-AQ-10", "name": "Patparganj Industrial IoT Node", "lat": 28.6290, "lon": 77.3020, "base_pm25": 174.0},
    {"id": "DEL-AQ-11", "name": "Noida Sector 62 Border Station", "lat": 28.6250, "lon": 77.3650, "base_pm25": 122.0},
    {"id": "DEL-AQ-12", "name": "Jahangirpuri Station", "lat": 28.7330, "lon": 77.1720, "base_pm25": 182.0},
]


def pm25_to_aqi(pm25: float) -> Tuple[int, str]:
    """
    Computes Air Quality Index and category according to Indian National AQI breakpoints.
    """
    # Breakpoints: (pm_low, pm_high, aqi_low, aqi_high)
    breakpoints = [
        (0.0, 30.0, 0, 50, "Good"),
        (30.1, 60.0, 51, 100, "Satisfactory"),
        (60.1, 90.0, 101, 200, "Moderate"),
        (90.1, 120.0, 201, 300, "Poor"),
        (120.1, 250.0, 301, 400, "Very Poor"),
        (250.1, 999.0, 401, 500, "Severe"),
    ]
    
    for c_low, c_high, i_low, i_high, category in breakpoints:
        if c_low <= pm25 <= c_high:
            aqi = int(((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low)
            return aqi, category
            
    return 500, "Severe"


def get_nearby_sensors(
    user_lat: float,
    user_lon: float,
    active_plume_geometries: List[Dict] = None,
) -> Tuple[float, int, str, List[NearbySensor]]:
    """
    Returns nearby sensors, interpolated PM2.5, AQI, and AQI category at (user_lat, user_lon).
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    sensor_distances: List[Tuple[float, Dict]] = []
    
    for st in CAAQMS_STATIONS:
        dist_m = calculate_distance_meters(user_lat, user_lon, st["lat"], st["lon"])
        dist_km = round(dist_m / 1000.0, 2)
        sensor_distances.append((dist_km, st))
        
    sensor_distances.sort(key=lambda x: x[0])
    top_sensors = sensor_distances[:5]
    
    # Calculate IDW (Inverse Distance Weighting) for street-level PM2.5
    weight_sum = 0.0
    pm_sum = 0.0
    
    sensor_models: List[NearbySensor] = []
    for dist_km, st in top_sensors:
        pm = st["base_pm25"]
        # Weighting: 1 / (d + 0.1)^2
        w = 1.0 / ((dist_km + 0.15) ** 2)
        weight_sum += w
        pm_sum += pm * w
        
        aqi_val, _ = pm25_to_aqi(pm)
        sensor_models.append(
            NearbySensor(
                sensor_id=st["id"],
                name=st["name"],
                latitude=st["lat"],
                longitude=st["lon"],
                distance_km=dist_km,
                pm25=round(pm, 1),
                aqi=aqi_val,
                quality_flag="good",
                observed_at=now_iso,
            )
        )
        
    interpolated_pm25 = round(pm_sum / weight_sum, 1) if weight_sum > 0 else 125.0
    aqi, category = pm25_to_aqi(interpolated_pm25)
    
    return interpolated_pm25, aqi, category, sensor_models


def get_health_recommendations(aqi: int, is_inside_plume: bool) -> List[str]:
    """Provides actionable health advice tailored to environmental conditions."""
    recs = []
    if is_inside_plume:
        recs.append("CRITICAL: You are inside an active smoke plume. Remain indoors and seal windows and air intakes.")
        recs.append("Wear an N95/FFP2 respirator mask if stepping outside is unavoidable.")
        recs.append("Activate indoor HEPA air purifiers at maximum speed.")
        return recs
        
    if aqi > 300:
        recs.append("Avoid outdoor cardio activities and strenuous exertion.")
        recs.append("Vulnerable groups (children, elderly, asthmatics) must stay inside.")
        recs.append("Keep windows closed during early morning and late evening inversion hours.")
    elif aqi > 200:
        recs.append("Sensitive individuals should limit prolonged outdoor exposure.")
        recs.append("Use a protective mask when commuting along high-traffic corridors.")
    elif aqi > 100:
        recs.append("Air quality is moderate. Unusually sensitive people should consider reducing prolonged outdoor exertion.")
    else:
        recs.append("Air quality is satisfactory. Ideal conditions for outdoor activities.")
        
    return recs
