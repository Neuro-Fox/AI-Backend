from datetime import datetime
from utils import haversine_distance, calculate_speed, inside_polygon
import json
import os

class RuleBasedDetector:
    def __init__(self, config=None):
        """
        Initializes the detector with default or custom thresholds:
        - stationary_too_long: seconds at almost same location
        - max_speed: threshold speed in m/s
        - signal_drop: seconds with NO GPS update at all
        """
        self.last_locations = {}  # stores last known location and timestamp
        self.last_update = {}     # stores last GPS update timestamp
        self.config = config or {
            "stationary_too_long": 300,    # 5 minutes
            "max_speed": 15.0,             # m/s (~54 km/h)
            "signal_drop": 900             # 15 minutes
        }

        # Load restricted and allowed zones from JSON
        zones_file = "backend/sample_zones.json"
        if os.path.exists(zones_file):
            with open(zones_file) as f:
                zones = json.load(f)
                self.restricted_zones = zones.get("restricted", [])
                self.allowed_zones = zones.get("allowed", [])
        else:
            self.restricted_zones = []
            self.allowed_zones = []

    def detect(self, gps_data):
        """
        Detect all five rule-based anomalies for a single GPS point:
        - Signal Drop
        - Stationary Too Long
        - Restricted Zone Entry
        - Geofence Exit
        - Excessive Speed
        Returns a list of anomalies detected.
        """
        anomalies = []
        tid = gps_data["tourist_id"]
        lat, lon = gps_data["lat"], gps_data["lon"]
        ts = datetime.fromisoformat(gps_data["ts"])

        # Signal Drop (no GPS update for too long)
        if tid in self.last_update:
            delta_since_last = (ts - self.last_update[tid]).total_seconds()
            if delta_since_last > self.config["signal_drop"]:
                anomalies.append("Signal Drop")
        self.last_update[tid] = ts

        # Stationary Too Long, Excessive Speed
        if tid in self.last_locations:
            prev = self.last_locations[tid]
            prev_lat, prev_lon, prev_ts = prev["lat"], prev["lon"], prev["ts"]
            dist = haversine_distance(prev_lat, prev_lon, lat, lon)
            delta_time = (ts - prev_ts).total_seconds()

            # Stationary Too Long
            if dist < 5 and delta_time > self.config["stationary_too_long"]:
                anomalies.append("Stationary Too Long")

            # Excessive Speed
            speed = calculate_speed(prev_lat, prev_lon, lat, lon, prev_ts, ts)
            if speed > self.config["max_speed"]:
                anomalies.append("Excessive Speed")

        # Restricted Zone Entry
        for zone in self.restricted_zones:
            if inside_polygon(lat, lon, zone):
                anomalies.append("Restricted Zone Entry")
                break

        # Geofence Exit
        inside_allowed = any(inside_polygon(lat, lon, zone) for zone in self.allowed_zones)
        if not inside_allowed:
            anomalies.append("Geofence Exit")

        # Save current location
        self.last_locations[tid] = {"lat": lat, "lon": lon, "ts": ts}

        return anomalies