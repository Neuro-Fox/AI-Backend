import math
from shapely.geometry import Point, Polygon

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371e3
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def calculate_speed(lat1, lon1, lat2, lon2, t1, t2):
    dist = haversine_distance(lat1, lon1, lat2, lon2)
    delta_time = (t2 - t1).total_seconds()
    if delta_time == 0:
        return 0
    return dist / delta_time

def inside_polygon(lat, lon, zone):
    """
    Checks if a (lat, lon) point is inside a given zone.
    zone: dict with keys "name" and "polygon"
    """
    polygon_coords = zone.get("polygon", [])
    polygon_coords = [(float(p[0]), float(p[1])) for p in polygon_coords]  # ensure floats
    polygon = Polygon(polygon_coords)
    point = Point(lat, lon)
    return polygon.contains(point)