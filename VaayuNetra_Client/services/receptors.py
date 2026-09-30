"""Socket 5: Vulnerable Receptors Service (Overpass QL OSM Geospatial Adapter).

Queries OpenStreetMap Overpass API asynchronously to identify sensitive and vulnerable community
infrastructure (schools, hospitals, clinics) intersecting the downwind plume cone polygon.
Calculates a composite vulnerability impact score with strict timeout and automatic local fallback.
"""

from typing import Any, Dict, List
import asyncio
import datetime
import logging
import httpx

logger = logging.getLogger(__name__)

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"

# Default fallback receptors if Overpass times out or has no network access
FALLBACK_RECEPTORS = [
    {
        "id": "mock-hosp-01",
        "name": "Sanjivani Community Health Center",
        "amenity": "hospital",
        "latitude": 28.6250,
        "longitude": 77.2180,
        "type": "hospital",
        "weight": 30,
    },
    {
        "id": "mock-sch-01",
        "name": "Sarvodaya Public Model School",
        "amenity": "school",
        "latitude": 28.6295,
        "longitude": 77.2240,
        "type": "school",
        "weight": 25,
    },
    {
        "id": "mock-clin-01",
        "name": "Sector Primary Healthcare Clinic",
        "amenity": "clinic",
        "latitude": 28.6310,
        "longitude": 77.2310,
        "type": "clinic",
        "weight": 20,
    },
]


def _extract_outer_ring(plume_coords: Any) -> List[List[float]]:
    """Extract a 2D list of [lon, lat] coordinates from GeoJSON polygon coordinates."""
    if not plume_coords or not isinstance(plume_coords, list):
        return []

    # If format is [[[lon, lat], ...]] (GeoJSON Polygon coordinates)
    if len(plume_coords) > 0 and isinstance(plume_coords[0], list):
        if len(plume_coords[0]) > 0 and isinstance(plume_coords[0][0], list):
            return plume_coords[0]
        return plume_coords

    return []


def _calculate_score(receptors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate composite vulnerability score based on receptor weights."""
    if not receptors:
        return {
            "score": 10.0,
            "level": "Low",
            "advisory": "Minimal critical infrastructure in downwind plume corridor.",
        }

    total_weight = 0
    for r in receptors:
        amenity = r.get("amenity", "").lower()
        if "hospital" in amenity:
            total_weight += 30
        elif "school" in amenity or "kindergarten" in amenity:
            total_weight += 25
        elif "clinic" in amenity:
            total_weight += 20
        else:
            total_weight += 15

    # Scale and cap score to [0, 100]
    score = min(100.0, max(15.0, float(total_weight)))

    if score >= 70.0:
        level = "Critical"
        advisory = "Immediate evacuation alert recommended for schools and healthcare centers downwind."
    elif score >= 40.0:
        level = "High"
        advisory = "Issue indoor shelter advisory with air filtration for downwind educational and medical institutions."
    else:
        level = "Moderate"
        advisory = "Standard advisory for vulnerable populations within plume projection zone."

    return {
        "score": round(score, 1),
        "level": level,
        "advisory": advisory,
    }


async def get_vulnerable_receptors(
    plume_coords: Any,
    timeout_seconds: float = 2.5,
) -> Dict[str, Any]:
    """Identify vulnerable community receptors (schools, hospitals, clinics) within plume polygon asynchronously.

    Args:
        plume_coords: GeoJSON Polygon coordinates list (ring of [lon, lat] pairs).
        timeout_seconds: Overpass request timeout cap in seconds (default 2.5s).

    Returns:
        Structured dictionary containing vulnerability_score, level, counts,
        and categorized receptor list.
    """
    ring = _extract_outer_ring(plume_coords)

    # Derive baseline coordinates from ring for fallback positioning
    fallback_lat = ring[0][1] if ring and len(ring) > 0 else 28.6139
    fallback_lon = ring[0][0] if ring and len(ring) > 0 else 77.2090

    # Fallback response generator
    def build_fallback(error_msg: str = "") -> Dict[str, Any]:
        localized_fallbacks = []
        for idx, base in enumerate(FALLBACK_RECEPTORS[:2], start=1):
            offset = 0.005 * idx
            localized_fallbacks.append({
                "id": f"rec-fallback-{idx}",
                "name": base["name"],
                "amenity": base["amenity"],
                "latitude": round(fallback_lat + offset, 5),
                "longitude": round(fallback_lon + offset, 5),
            })

        score_meta = _calculate_score(localized_fallbacks)
        return {
            "vulnerability_score": score_meta["score"],
            "risk_level": score_meta["level"],
            "advisory": score_meta["advisory"],
            "total_receptors": len(localized_fallbacks),
            "receptors": localized_fallbacks,
            "source": "fallback_mock",
            "error": error_msg or None,
        }

    # Validate coordinate ring
    if len(ring) < 3:
        logger.warning("Invalid plume polygon ring provided, falling back.")
        return build_fallback("Insufficient polygon points for Overpass query")

    # Format Overpass poly string: "lat1 lon1 lat2 lon2 ..."
    # Remove duplicate closing point if present
    points = ring[:-1] if (len(ring) > 1 and ring[0] == ring[-1]) else ring
    poly_terms = []
    for pt in points:
        lon_val, lat_val = pt[0], pt[1]
        poly_terms.append(f"{lat_val:.6f} {lon_val:.6f}")
    poly_str = " ".join(poly_terms)

    # Overpass QL query with matching 2s timeout
    overpass_query = f"""
    [out:json][timeout:2];
    (
      node["amenity"~"school|hospital|clinic|kindergarten"](poly:"{poly_str}");
      way["amenity"~"school|hospital|clinic|kindergarten"](poly:"{poly_str}");
    );
    out center;
    """

    headers = {
        "User-Agent": "VaayuNetra/2.0 (AtmosphericIntelligence; mailto:contact@vaayunetra.org)",
    }

    async def _fetch():
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds)) as client:
            response = await client.post(
                OVERPASS_API_URL,
                data={"data": overpass_query},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            elements = data.get("elements", [])

            receptors: List[Dict[str, Any]] = []
            for el in elements:
                tags = el.get("tags", {})
                name = tags.get("name") or tags.get("name:en") or f"Unnamed {tags.get('amenity', 'Facility')}"
                amenity = tags.get("amenity", "community_facility")

                lat_val = el.get("lat") or el.get("center", {}).get("lat")
                lon_val = el.get("lon") or el.get("center", {}).get("lon")

                if lat_val is not None and lon_val is not None:
                    receptors.append({
                        "id": str(el.get("id")),
                        "name": name,
                        "amenity": amenity,
                        "latitude": round(float(lat_val), 5),
                        "longitude": round(float(lon_val), 5),
                    })

            if receptors:
                score_meta = _calculate_score(receptors)
                return {
                    "vulnerability_score": score_meta["score"],
                    "risk_level": score_meta["level"],
                    "advisory": score_meta["advisory"],
                    "total_receptors": len(receptors),
                    "receptors": receptors,
                    "source": "overpass_live",
                }
            else:
                return build_fallback("No institutions detected in exact polygon footprint")

    try:
        return await asyncio.wait_for(_fetch(), timeout=timeout_seconds)
    except (httpx.TimeoutException, asyncio.TimeoutError) as exc:
        logger.warning(
            "Overpass API timed out after %.1fs (%s). Returning synthetic fallback receptors.",
            timeout_seconds,
            exc,
        )
        return build_fallback("Overpass query timed out")
    except Exception as exc:
        logger.warning(
            "Overpass API query failed (%s: %s). Returning synthetic fallback receptors.",
            type(exc).__name__,
            exc,
        )
        return build_fallback(str(exc))
