"""Socket 1: Weather Service - Live Wind Vector and Atmospheric Conditions.

Queries Open-Meteo API asynchronously for real-time wind speed, wind direction, temperature,
and relative humidity, with automatic failover to baseline meteorological defaults within 2.5s.
"""

from typing import Any, Dict
import logging
import httpx

logger = logging.getLogger(__name__)

FALLBACK_WEATHER: Dict[str, Any] = {
    "wind_speed_10m": 12.0,
    "wind_direction_10m": 220.0,
    "temperature_2m": 28.0,
    "relative_humidity_2m": 60.0,
    "source": "fallback",
    "status": "fallback_activated",
}


async def get_live_weather(lat: float, lon: float, timeout_seconds: float = 2.5) -> Dict[str, Any]:
    """Fetch live wind vector and atmospheric conditions from Open-Meteo asynchronously.

    Args:
        lat: Latitude in decimal degrees.
        lon: Longitude in decimal degrees.
        timeout_seconds: Request timeout cap in seconds (default 2.5s).

    Returns:
        Dict containing wind_speed_10m, wind_direction_10m, temperature_2m,
        relative_humidity_2m, and source flag.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
    )

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds)) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            current = data.get("current", {})

            wind_speed = current.get("wind_speed_10m")
            wind_direction = current.get("wind_direction_10m")
            temperature = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")

            if wind_speed is None or wind_direction is None:
                logger.warning("Open-Meteo missing key weather fields, falling back.")
                return {**FALLBACK_WEATHER, "error": "Missing key parameters in response"}

            return {
                "wind_speed_10m": float(wind_speed),
                "wind_direction_10m": float(wind_direction),
                "temperature_2m": float(temperature) if temperature is not None else 28.0,
                "relative_humidity_2m": float(humidity) if humidity is not None else 60.0,
                "source": "open-meteo",
                "status": "live",
            }

    except httpx.TimeoutException as exc:
        logger.warning("Open-Meteo timed out after %.1fs (%s). Using fallback weather.", timeout_seconds, exc)
        return {
            **FALLBACK_WEATHER,
            "error": "Open-Meteo query timed out",
        }
    except Exception as exc:
        logger.warning("Open-Meteo query failed (%s: %s). Using fallback weather.", type(exc).__name__, exc)
        return {
            **FALLBACK_WEATHER,
            "error": str(exc),
        }
