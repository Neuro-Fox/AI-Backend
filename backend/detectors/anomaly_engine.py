from .rule_detector import RuleBasedDetector
from .ai_detector import AIDetector
from datetime import datetime, timedelta

class AnomalyEngine:
    def __init__(self):
        self.rule_detector = RuleBasedDetector()
        self.ai_detector = AIDetector()

    def process_gps(self, gps_data):
        tid = gps_data["tourist_id"]

        # Rule-based anomalies
        anomalies = self.rule_detector.detect(gps_data)

        # AI-based anomalies
        features = [gps_data["lat"], gps_data["lon"]]
        ai_results = self.ai_detector.detect(gps_data, features)
        risk_prob = ai_results.get("risk_prob")
        next_loc = ai_results.get("next_location")

        # Optional safety score
        safety_score = int((1 - risk_prob) * 100) if risk_prob is not None else None

        response = {
            "tourist_id": tid,
            "timestamp": gps_data["ts"],
            "current_location": {"lat": gps_data["lat"], "lon": gps_data["lon"]},
            "anomalies_detected": anomalies,
            "risk_probability": risk_prob,
            "safety_score": safety_score,
            "next_expected_location": {"lat": float(next_loc[0]), "lon": float(next_loc[1])} if next_loc else None,
            "next_expected_time": (datetime.fromisoformat(gps_data["ts"]) + timedelta(minutes=10)).isoformat(),
            "alert": len(anomalies) > 0
        }

        return response