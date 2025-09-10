import pickle
import numpy as np
import os
import pandas as pd

# Simple fallback LSTM
class DummyLSTM:
    def predict(self, X):
        X = np.array(X)
        return np.array([[X[0][0] + 0.001, X[0][1] + 0.001]])

class AIDetector:
    def __init__(self):
        # Load Isolation Forest
        try:
            self.if_model = pickle.load(open("models/isolation_forest.pkl", "rb"))
            self.if_features = getattr(self.if_model, "feature_names_in_", ["lat", "lon"])
        except Exception:
            self.if_model = None
            self.if_features = ["lat", "lon"]

        # Load Risk Model
        try:
            self.risk_model = pickle.load(open("models/risk_model.pkl", "rb"))
            self.risk_features = getattr(self.risk_model, "feature_names_in_", ["lat", "lon"])
        except Exception:
            self.risk_model = None
            self.risk_features = ["lat", "lon"]

        # Handle LSTM safely
        try:
            if os.path.exists("models/lstm_trajectory.pkl"):
                with open("models/lstm_trajectory.pkl", "rb") as f:
                    data = f.read()
                if data == b"DUMMY":  # marker file instead of pickled object
                    self.lstm_model = DummyLSTM()
                else:
                    self.lstm_model = pickle.loads(data)
            else:
                self.lstm_model = DummyLSTM()
        except Exception:
            self.lstm_model = DummyLSTM()

    def detect(self, gps_data, history_features):
        results = {}

        # Convert history_features to DataFrame with proper column names
        features_if = pd.DataFrame([history_features], columns=self.if_features)
        features_risk = pd.DataFrame([history_features], columns=self.risk_features)

        # Isolation Forest score
        if self.if_model:
            try:
                results["iso_score"] = float(self.if_model.score_samples(features_if)[0])
            except Exception:
                results["iso_score"] = None
        else:
            results["iso_score"] = None

        # Risk probability
        if self.risk_model:
            try:
                results["risk_prob"] = float(self.risk_model.predict_proba(features_risk)[0][1])
            except Exception:
                results["risk_prob"] = None
        else:
            results["risk_prob"] = None

        # Next location prediction
        try:
            results["next_location"] = self.lstm_model.predict(np.array([history_features]))[0].tolist()
        except Exception:
            results["next_location"] = None

        return results