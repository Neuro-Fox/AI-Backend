

from datetime import datetime
from utils import haversine_distance, calculate_speed, inside_polygon, snap_to_roads, get_route_polyline, check_route_deviation
import json
import os

class RuleBasedDetector:
    def __init__(self, config=None):
        self.last_locations = {}
        self.last_update = {}
        self.route_polyline = None

        self.config = config or {
            "stationary_too_long": 300,
            "max_speed": 15.0,
            "signal_drop": 900,
            "max_route_deviation": 200
        }

        zones_file = "backend/sample_zones.json"
        if os.path.exists(zones_file):
            with open(zones_file) as f:
                zones = json.load(f)
                self.restricted_zones = zones.get("restricted", [])
                self.allowed_zones = zones.get("allowed", [])
                origin = zones.get("route_origin")
                destination = zones.get("route_destination")
                if origin and destination:
                    self.route_polyline = get_route_polyline(origin, destination)
        else:
            self.restricted_zones = []
            self.allowed_zones = []

    def detect(self, gps_data):
        anomalies = []
        tid = gps_data["tourist_id"]
        ts = datetime.fromisoformat(gps_data["ts"])

        # Signal Drop
        if tid in self.last_update:
            delta = (ts - self.last_update[tid]).total_seconds()
            if delta > self.config["signal_drop"]:
                anomalies.append("Signal Drop")
        self.last_update[tid] = ts

        lat = gps_data.get("lat")
        lon = gps_data.get("lon")

        if lat is not None and lon is not None:
            # Snap GPS to nearest road
            snap_lat, snap_lon = snap_to_roads(lat, lon)

            # Stationary Too Long & Excessive Speed
            if tid in self.last_locations:
                prev = self.last_locations[tid]
                dist = haversine_distance(prev["lat"], prev["lon"], snap_lat, snap_lon)
                delta_time = (ts - prev["ts"]).total_seconds()

                if dist < 5 and delta_time > self.config["stationary_too_long"]:
                    anomalies.append("Stationary Too Long")

                speed = calculate_speed(prev["lat"], prev["lon"], snap_lat, snap_lon, prev["ts"], ts)
                if speed > self.config["max_speed"]:
                    anomalies.append("Excessive Speed")

            # Restricted Zone Entry
            for zone in self.restricted_zones:
                if inside_polygon(snap_lat, snap_lon, zone):
                    anomalies.append("Restricted Zone Entry")
                    break

            # Route Deviation using snapped point
            if self.route_polyline and check_route_deviation(snap_lat, snap_lon, self.route_polyline, self.config["max_route_deviation"]):
                anomalies.append("Route Deviation")

            # Save current location
            self.last_locations[tid] = {"lat": snap_lat, "lon": snap_lon, "ts": ts}

        return anomalies



