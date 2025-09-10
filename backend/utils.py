import math
from shapely.geometry import Point, Polygon ,LineString
import requests
import polyline

GOOGLE_API_KEY = "AIzaSyB-8jErYrelIyRc0ftL0VR1C4GvS6ILSr8"



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


def get_route_polyline(origin: str, destination: str):
    """
    Get route polyline from Google Directions API.
    origin, destination: strings like "28.614,77.209"
    returns: list of (lat, lon) points or []
    """
    url = (
        f"https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={origin}&destination={destination}&key={GOOGLE_API_KEY}"
    )
    res = requests.get(url).json()

    if res.get("status") != "OK":
        print("Google Directions API error:", res.get("status"), res.get("error_message"))
        return []

    routes = res.get("routes", [])
    if routes:
        encoded = routes[0]["overview_polyline"]["points"]
        dash=polyline.decode(encoded)
        print(dash)
        return dash

    return []

def snap_to_roads(lat, lon):
    """Snap GPS point to nearest road using Google Roads API"""
    try:
        url = f"https://roads.googleapis.com/v1/snapToRoads?path={lat},{lon}&key={GOOGLE_API_KEY}"
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        if "snappedPoints" in data and len(data["snappedPoints"]) > 0:
            loc = data["snappedPoints"][0]["location"]
            return loc["latitude"], loc["longitude"]
    except Exception as e:
        print(f"Snap to road error: {e}")
    return lat, lon

def check_route_deviation(lat, lon, route_polyline, threshold=200):
    """Check if GPS point deviates more than threshold meters from route"""
    if not route_polyline:
        return False
    point = Point(lon, lat)
    line = LineString([(lng, lat) for lat, lng in route_polyline])
    distance_m = point.distance(line) * 111139
    return distance_m > threshold


def calculate_trip_safety_score(self, tid):
    events = self.trip_events.get(tid, [])
    if not events:
        return 100

    anomaly_weight = {
        "Stationary Too Long": 1,
        "Excessive Speed": 2,
        "Restricted Zone Entry": 5,
        "Route Deviation": 3,
        "Signal Drop": 2,
    }

    total_risk = 0
    for event in events:
        for anomaly in event["anomalies"]:
            total_risk += anomaly_weight.get(anomaly, 1)

    max_possible_risk = len(events) * max(anomaly_weight.values())
    safety_score = max(0, 100 - (total_risk / max_possible_risk) * 100)
    return safety_score