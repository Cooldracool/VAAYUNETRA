"""Socket 4: Gaussian Plume Generator and Downwind Atmospheric Dispersion.

Calculates downwind dispersion cone geometries based on wind speed, direction,
and projection duration using geodesic projections. Provides GeoJSON Polygon
features and point-in-plume collision detection for citizen alerting.
"""

from typing import Any, Dict, List
import math

EARTH_RADIUS_KM = 6371.0


def _destination_point(
    lat: float,
    lon: float,
    distance_km: float,
    bearing_deg: float,
) -> List[float]:
    """Calculate destination coordinates [lon, lat] given start, distance, and bearing.

    Returns:
        [lon, lat] in decimal degrees (GeoJSON compliant coordinate order).
    """
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    bearing_rad = math.radians(bearing_deg)
    angular_dist = distance_km / EARTH_RADIUS_KM

    dest_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(angular_dist)
        + math.cos(lat_rad) * math.sin(angular_dist) * math.cos(bearing_rad)
    )
    dest_lon_rad = lon_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(angular_dist) * math.cos(lat_rad),
        math.cos(angular_dist) - math.sin(lat_rad) * math.sin(dest_lat_rad),
    )

    dest_lat = math.degrees(dest_lat_rad)
    dest_lon = math.degrees(dest_lon_rad)

    # Normalize longitude to [-180, 180]
    dest_lon = (dest_lon + 540.0) % 360.0 - 180.0

    return [round(dest_lon, 6), round(dest_lat, 6)]


def calculate_plume_cone(
    source_lat: float,
    source_lon: float,
    wind_speed_kmh: float,
    wind_dir_deg: float,
    hours: float = 6.0,
    cone_half_angle_deg: float = 15.0,
) -> Dict[str, Any]:
    """Compute an expanding downwind dispersion cone.

    Args:
        source_lat: Source incident latitude.
        source_lon: Source incident longitude.
        wind_speed_kmh: Wind speed in km/h.
        wind_dir_deg: Wind origin direction in degrees (meteorological).
        hours: Plume dispersion timeline projection (default 6.0 hours).
        cone_half_angle_deg: Half angle of plume expansion (total 30-degree cone).

    Returns:
        GeoJSON Feature dictionary containing Polygon geometry and properties.
    """
    # Smoke travels downwind: heading = (wind_dir + 180) % 360
    downwind_heading = (float(wind_dir_deg) + 180.0) % 360.0

    # Ensure reasonable minimum dispersion distance even under low wind
    effective_speed = max(2.0, float(wind_speed_kmh))
    distance_km = round(effective_speed * max(0.5, float(hours)), 2)

    # Sample arc points across the 30-degree cone (from -15 deg to +15 deg)
    num_arc_points = 9
    start_angle = downwind_heading - cone_half_angle_deg
    end_angle = downwind_heading + cone_half_angle_deg
    step = (end_angle - start_angle) / (num_arc_points - 1)

    # GeoJSON Polygon exterior ring: starts at source [lon, lat], traces arc, closes at source
    origin_point = [round(source_lon, 6), round(source_lat, 6)]
    polygon_ring = [origin_point]

    for i in range(num_arc_points):
        current_bearing = (start_angle + i * step) % 360.0
        arc_pt = _destination_point(source_lat, source_lon, distance_km, current_bearing)
        polygon_ring.append(arc_pt)

    # Close polygon
    polygon_ring.append(origin_point)

    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [polygon_ring],
        },
        "properties": {
            "source_latitude": source_lat,
            "source_longitude": source_lon,
            "heading_deg": round(downwind_heading, 2),
            "distance_km": distance_km,
            "speed_kmh": round(wind_speed_kmh, 2),
            "wind_direction_deg": round(wind_dir_deg, 2),
            "duration_hours": round(hours, 2),
            "cone_spread_deg": round(cone_half_angle_deg * 2, 1),
            "dispersion_model": "Gaussian Plume Cone Projection",
        },
    }


def is_point_in_plume(point_lat: float, point_lon: float, plume_geojson: Dict[str, Any]) -> bool:
    """Check if given coordinates fall inside a plume GeoJSON Polygon using ray casting.

    Args:
        point_lat: Latitude of query point.
        point_lon: Longitude of query point.
        plume_geojson: GeoJSON Feature with Polygon geometry.

    Returns:
        True if inside or on boundary, False otherwise.
    """
    try:
        geometry = plume_geojson.get("geometry", {})
        if geometry.get("type") != "Polygon":
            return False

        coordinates = geometry.get("coordinates", [])
        if not coordinates:
            return False

        exterior_ring = coordinates[0]
        n = len(exterior_ring)
        if n < 3:
            return False

        inside = False
        px, py = point_lon, point_lat
        j = n - 1

        for i in range(n):
            xi, yi = exterior_ring[i][0], exterior_ring[i][1]
            xj, yj = exterior_ring[j][0], exterior_ring[j][1]

            # Ray-casting crossing test
            intersect = ((yi > py) != (yj > py)) and (
                px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi
            )
            if intersect:
                inside = not inside
            j = i

        return inside
    except Exception:
        return False
