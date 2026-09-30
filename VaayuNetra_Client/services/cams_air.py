"""Socket 6: Regional Atmospheric Context Service (Open-Meteo Air Quality / CAMS).

Queries the Copernicus Atmosphere Monitoring Service (CAMS) / Open-Meteo Air Quality API
asynchronously for upper-air column metrics:
- Nitrogen Dioxide (NO2): Indicative of vehicular combustion & industrial fossil fuels
- Aerosol Optical Depth (AOD): Indicative of total vertical particulate column & biomass burning

Classifies the regional air column with strict 2.5s timeout caps and instant fallback.
"""

from typing import Any, Dict
import datetime
import logging
import httpx

logger = logging.getLogger(__name__)

AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

FALLBACK_ATMOSPHERE: Dict[str, Any] = {
    "pm2_5": 115.0,
    "nitrogen_dioxide": 28.5,
    "aerosol_optical_depth": 0.74,
    "air_column_classification": "Biomass Burning Plume / High Optical Depth",
    "primary_pollutant_driver": "Aerosols & Suspended Particulates",
    "atmospheric_inversion_risk": "High",
    "interpretation": "High aerosol optical depth (>0.6) combined with moderate NO2 indicates strong biomass burning / stubble fire transport.",
    "source": "fallback",
    "status": "fallback_activated",
}


def _classify_air_column(no2: float, aod: float, pm25: float) -> Dict[str, str]:
    """Classify the atmospheric column based on chemical and optical markers."""
    if aod >= 0.60 and no2 < 45.0:
        classification = "Biomass Burning Plume / High Optical Depth"
        driver = "Agricultural Stubble / Biomass Burning"
        inversion = "High"
        interp = (
            f"Aerosol Optical Depth is elevated (AOD={aod:.2f}) with moderate NO2 ({no2:.1f} µg/m³), "
            f"confirming strong biomass burning smoke transport."
        )
    elif aod >= 0.60 and no2 >= 45.0:
        classification = "Severe Compound Atmospheric Inversion (Biomass + Heavy Urban Traffic)"
        driver = "Compound Multi-Sectoral (Vehicular & Biomass)"
        inversion = "Critical"
        interp = (
            f"Both AOD ({aod:.2f}) and NO2 ({no2:.1f} µg/m³) are critically elevated, "
            f"signaling dense smoke interacting with trapped urban vehicular exhaust."
        )
    elif aod < 0.60 and no2 >= 45.0:
        classification = "Urban Traffic & Industrial Smog"
        driver = "Combustion Exhaust & Nitrous Compounds"
        inversion = "Moderate"
        interp = (
            f"Elevated NO2 ({no2:.1f} µg/m³) with moderate AOD ({aod:.2f}) "
            f"points to surface-level vehicular emissions and fossil fuel combustion."
        )
    else:
        classification = "Moderate Regional Background Haze"
        driver = "Ambient Particulate Mixture"
        inversion = "Low"
        interp = f"Regional air column is relatively stable with AOD={aod:.2f} and NO2={no2:.1f} µg/m³."

    return {
        "classification": classification,
        "driver": driver,
        "inversion": inversion,
        "interpretation": interp,
    }


async def get_atmospheric_context(
    lat: float,
    lon: float,
    timeout_seconds: float = 2.5,
) -> Dict[str, Any]:
    """Retrieve atmospheric air column context including NO2 and AOD metrics asynchronously.

    Args:
        lat: Latitude in decimal degrees.
        lon: Longitude in decimal degrees.
        timeout_seconds: API request timeout cap in seconds (default 2.5s).

    Returns:
        Structured dictionary containing NO2, AOD, PM2.5, and classification.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm2_5,nitrogen_dioxide,aerosol_optical_depth",
        "forecast_days": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds)) as client:
            response = await client.get(AIR_QUALITY_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            hourly = data.get("hourly", {})

            times = hourly.get("time", [])
            no2_series = hourly.get("nitrogen_dioxide", [])
            aod_series = hourly.get("aerosol_optical_depth", [])
            pm25_series = hourly.get("pm2_5", [])

            if not times or not no2_series or not aod_series:
                logger.warning("Open-Meteo Air Quality response missing hourly data, using fallback.")
                return {**FALLBACK_ATMOSPHERE, "error": "Incomplete hourly telemetry"}

            # Find index for current UTC hour
            now_hour_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:00")
            target_idx = 0
            if now_hour_str in times:
                target_idx = times.index(now_hour_str)

            # Extract values with safe forward scanning if null
            def _get_val(series: list, idx: int, default_val: float) -> float:
                val = series[idx] if idx < len(series) else None
                if val is not None:
                    return float(val)
                for v in series:
                    if v is not None:
                        return float(v)
                return default_val

            cur_no2 = _get_val(no2_series, target_idx, 28.5)
            cur_aod = _get_val(aod_series, target_idx, 0.74)
            cur_pm25 = _get_val(pm25_series, target_idx, 115.0)

            diag = _classify_air_column(cur_no2, cur_aod, cur_pm25)

            return {
                "pm2_5": round(cur_pm25, 1),
                "nitrogen_dioxide": round(cur_no2, 2),
                "aerosol_optical_depth": round(cur_aod, 3),
                "air_column_classification": diag["classification"],
                "primary_pollutant_driver": diag["driver"],
                "atmospheric_inversion_risk": diag["inversion"],
                "interpretation": diag["interpretation"],
                "timestamp": times[target_idx] if target_idx < len(times) else now_hour_str,
                "source": "open-meteo-cams-live",
                "status": "live",
            }

    except httpx.TimeoutException as exc:
        logger.warning(
            "Air Quality API request timed out after %.1fs (%s). Using safe atmospheric fallback.",
            timeout_seconds,
            exc,
        )
        return {
            **FALLBACK_ATMOSPHERE,
            "error": "Air Quality API query timed out",
        }
    except Exception as exc:
        logger.info(
            "Air Quality API query failed (%s: %s). Using safe atmospheric fallback.",
            type(exc).__name__,
            exc,
        )
        return {
            **FALLBACK_ATMOSPHERE,
            "error": str(exc),
        }
