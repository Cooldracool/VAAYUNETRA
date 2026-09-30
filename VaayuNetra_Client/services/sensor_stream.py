"""Socket 3: Ground IoT Baseline Sensor Stream.

Integrates real-time ambient particulate sensor feeds from the Sensor.Community
crowdsourced network, with high-resilience synthetic fallback generation to ensure
continuous IoT baseline availability and sub-2s response caps.
"""

from typing import Any, Dict, List
import asyncio
import datetime
import logging
import math
import httpx

logger = logging.getLogger(__name__)

SENSOR_COMMUNITY_URL = "https://data.sensor.community/static/v2/data.json"


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in km."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 2)


def generate_synthetic_sensors(lat: float, lon: float) -> List[Dict[str, Any]]:
    """Generate 3 localized synthetic IoT nodes around (lat, lon) with realistic PM2.5/PM10."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # Baseline PM2.5 around 138 µg/m³ (biomass burning / urban spike)
    offsets = [
        {"dlat": 0.0042, "dlon": 0.0031, "name": "Node-VN-Alpha", "pm25": 138.4, "pm10": 194.2},
        {"dlat": -0.0051, "dlon": 0.0068, "name": "Node-VN-Beta", "pm25": 142.1, "pm10": 208.5},
        {"dlat": 0.0083, "dlon": -0.0044, "name": "Node-VN-Gamma", "pm25": 126.8, "pm10": 175.0},
    ]

    nodes: List[Dict[str, Any]] = []
    for idx, off in enumerate(offsets, start=1):
        s_lat = round(lat + off["dlat"], 5)
        s_lon = round(lon + off["dlon"], 5)
        dist_km = _haversine_km(lat, lon, s_lat, s_lon)
        nodes.append({
            "sensor_id": f"VN-IOT-{100 + idx}",
            "label": off["name"],
            "latitude": s_lat,
            "longitude": s_lon,
            "distance_km": dist_km,
            "pm2_5": off["pm25"],
            "pm10": off["pm10"],
            "aqi_category": "Very Unhealthy" if off["pm25"] > 100 else "Moderate",
            "timestamp": now_iso,
            "source": "synthetic_baseline",
        })

    return nodes


async def get_nearby_sensors(
    lat: float,
    lon: float,
    radius_km: float = 15.0,
    timeout_seconds: float = 2.0,
) -> List[Dict[str, Any]]:
    """Fetch nearby sensor data from Sensor.Community asynchronously or return 3 localized synthetic nodes.

    Args:
        lat: Latitude in decimal degrees.
        lon: Longitude in decimal degrees.
        radius_km: Search radius in kilometers.
        timeout_seconds: Request timeout cap in seconds (strict 2.0s).

    Returns:
        List of sensor reading dicts.
    """
    try:
        delta_lat = radius_km / 111.0
        cos_lat = math.cos(math.radians(lat))
        delta_lon = radius_km / (111.0 * max(0.1, cos_lat))

        min_lat, max_lat = lat - delta_lat, lat + delta_lat
        min_lon, max_lon = lon - delta_lon, lon + delta_lon

        async def _fetch():
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds)) as client:
                resp = await client.get(SENSOR_COMMUNITY_URL)
                if resp.status_code == 200:
                    raw_data = resp.json()
                    sensors_found: List[Dict[str, Any]] = []

                    for entry in raw_data:
                        location = entry.get("location", {})
                        slat_str = location.get("latitude")
                        slon_str = location.get("longitude")
                        if not slat_str or not slon_str:
                            continue

                        try:
                            slat = float(slat_str)
                            slon = float(slon_str)
                        except ValueError:
                            continue

                        if min_lat <= slat <= max_lat and min_lon <= slon <= max_lon:
                            pm25_val = None
                            pm10_val = None
                            for val in entry.get("sensordatavalues", []):
                                v_type = val.get("value_type")
                                v_str = val.get("value")
                                if v_type == "P2" and v_str is not None:
                                    try:
                                        pm25_val = float(v_str)
                                    except ValueError:
                                        pass
                                elif v_type == "P1" and v_str is not None:
                                    try:
                                        pm10_val = float(v_str)
                                    except ValueError:
                                        pass

                            if pm25_val is not None:
                                dist = _haversine_km(lat, lon, slat, slon)
                                sensors_found.append({
                                    "sensor_id": f"SC-{entry.get('id', 'anon')}",
                                    "label": f"SensorCommunity #{entry.get('id')}",
                                    "latitude": slat,
                                    "longitude": slon,
                                    "distance_km": dist,
                                    "pm2_5": pm25_val,
                                    "pm10": pm10_val if pm10_val is not None else pm25_val * 1.4,
                                    "timestamp": entry.get("timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat()),
                                    "source": "sensor_community_live",
                                })

                        if len(sensors_found) >= 10:
                            break

                    if sensors_found:
                        sensors_found.sort(key=lambda s: s["distance_km"])
                        return sensors_found
                return None

        result = await asyncio.wait_for(_fetch(), timeout=timeout_seconds)
        if result:
            return result

    except (httpx.TimeoutException, asyncio.TimeoutError) as exc:
        logger.warning(
            "Sensor.Community request timed out after %.1fs (%s). Returning synthetic baseline.",
            timeout_seconds,
            exc,
        )
    except Exception as exc:
        logger.warning(
            "Sensor.Community live feed unavailable (%s: %s). Activating synthetic fallback.",
            type(exc).__name__,
            exc,
        )

    # Fallback immediately to 3 localized nodes with realistic PM2.5 readings
    return generate_synthetic_sensors(lat, lon)
