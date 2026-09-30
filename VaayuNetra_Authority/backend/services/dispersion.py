import math
from typing import Any, Dict, List, Tuple
from shapely.geometry import Point, Polygon


def calculate_downwind_plume(
    origin_lat: float,
    origin_lon: float,
    wind_speed_mps: float,
    wind_direction_deg: float,
    severity: str = "HIGH",
    length_km: float = 3.5,
) -> Dict[str, Any]:
    """
    Computes a downwind Gaussian/advection dispersion plume polygon.
    
    Wind direction theta is the direction wind blows FROM.
    Plume travels TOWARDS (theta + 180) % 360.
    
    Returns GeoJSON geometry dict: {"type": "Polygon", "coordinates": [[[lon, lat], ...]]}
    """
    # Adjust length by severity and wind speed
    severity_mult = {
        "LOW": 0.6,
        "MODERATE": 0.85,
        "HIGH": 1.15,
        "CRITICAL": 1.45,
    }.get(severity.upper(), 1.0)
    
    effective_length_km = max(1.5, length_km * severity_mult * min(2.0, max(0.6, wind_speed_mps / 3.0)))
    
    # Plume travels in the direction the wind is blowing towards
    downwind_bearing_deg = (wind_direction_deg + 180.0) % 360.0
    downwind_rad = math.radians(downwind_bearing_deg)
    
    # Perpendicular bearing for plume spread (lateral axis)
    perp_rad = downwind_rad + math.pi / 2.0
    
    # Approximate degree conversions for Delhi latitude (~28.6 deg)
    km_per_lat = 111.132
    km_per_lon = 111.320 * math.cos(math.radians(origin_lat))
    
    # Generate points along the plume contour
    steps = 14
    right_points: List[List[float]] = []
    left_points: List[List[float]] = []
    
    # Source apex
    right_points.append([origin_lon, origin_lat])
    
    for i in range(1, steps + 1):
        fraction = i / steps
        downwind_dist = fraction * effective_length_km
        
        # Plume lateral half-width expanding with distance (Pasquill-Gifford dispersion profile)
        # Starts small at source, widens downwind, tapers slightly at edge
        spread_km = (0.28 * (downwind_dist ** 0.82) + 0.05) * (1.0 - 0.25 * (fraction ** 2))
        
        # Centerline position
        center_x_km = downwind_dist * math.sin(downwind_rad)
        center_y_km = downwind_dist * math.cos(downwind_rad)
        
        # Right flank (+ perpendicular)
        r_x = center_x_km + spread_km * math.sin(perp_rad)
        r_y = center_y_km + spread_km * math.cos(perp_rad)
        r_lon = origin_lon + r_x / km_per_lon
        r_lat = origin_lat + r_y / km_per_lat
        right_points.append([round(r_lon, 6), round(r_lat, 6)])
        
        # Left flank (- perpendicular)
        l_x = center_x_km - spread_km * math.sin(perp_rad)
        l_y = center_y_km - spread_km * math.cos(perp_rad)
        l_lon = origin_lon + l_x / km_per_lon
        l_lat = origin_lat + l_y / km_per_lat
        left_points.append([round(l_lon, 6), round(l_lat, 6)])
        
    # Plume tip rounded arc
    tip_center_dist = effective_length_km
    tip_x = tip_center_dist * math.sin(downwind_rad)
    tip_y = tip_center_dist * math.cos(downwind_rad)
    tip_lon = round(origin_lon + tip_x / km_per_lon, 6)
    tip_lat = round(origin_lat + tip_y / km_per_lat, 6)
    
    # Combine: right side -> tip -> reversed left side -> close polygon
    polygon_coords = right_points + [[tip_lon, tip_lat]] + left_points[::-1] + [[origin_lon, origin_lat]]
    
    return {
        "type": "Polygon",
        "coordinates": [polygon_coords],
    }


def is_point_inside_plume(lat: float, lon: float, plume_geojson: Dict[str, Any]) -> bool:
    """
    Evaluates whether the coordinate (lat, lon) is within the plume polygon.
    """
    try:
        coords = plume_geojson["coordinates"][0]
        # Polygon coordinates in GeoJSON are [lon, lat]
        shapely_poly = Polygon(coords)
        pt = Point(lon, lat)
        return shapely_poly.contains(pt) or shapely_poly.touches(pt)
    except Exception:
        # Fallback ray-casting if Shapely encountered topology issue
        return ray_cast_point_in_poly(lon, lat, coords)


def ray_cast_point_in_poly(x: float, y: float, poly: List[List[float]]) -> bool:
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def calculate_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance between two coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)


def get_bearing_cardinal(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    """Returns cardinal direction (N, NE, E, SE, etc.) from point 1 to point 2."""
    d_lon = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    y = math.sin(d_lon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(d_lon)
    bearing = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
    
    cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((bearing + 11.25) / 22.5) % 16
    return cardinals[idx]
