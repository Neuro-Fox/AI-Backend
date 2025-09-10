import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier

# Ensure models directory exists
os.makedirs("models", exist_ok=True)

# Load GPS data
gps_data = pd.read_csv("data/gps_stream.csv")

# Features
X = gps_data[["lat", "lon"]]

# Labels (if available, else default 0s)
if "anomaly_label" in gps_data.columns:
    y = gps_data["anomaly_label"]
else:
    y = [0] * len(gps_data)

# Train Isolation Forest
if_model = IsolationForest(contamination=0.05, random_state=42)
if_model.fit(X)
pickle.dump(if_model, open("models/isolation_forest.pkl", "wb"))

# Train Risk Model (Random Forest)
risk_model = RandomForestClassifier(n_estimators=50, random_state=42)
risk_model.fit(X, y)
pickle.dump(risk_model, open("models/risk_model.pkl", "wb"))

# Dummy LSTM placeholder
class DummyLSTM:
    def predict(self, X):
        X = np.array(X)
        return np.array([[X[0][0] + 0.001, X[0][1] + 0.001]])

pickle.dump(DummyLSTM(), open("models/lstm_trajectory.pkl", "wb"))

print("Models trained and saved in /models/")