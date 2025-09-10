from fastapi import FastAPI, Request
from detectors.anomaly_engine import AnomalyEngine
import uvicorn
from fastapi.responses import JSONResponse
from typing import Optional
import json
import os

app = FastAPI()
engine = AnomalyEngine()
LOG_FILE = "logs/alerts.json"  # Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

@app.post("/ingest")
async def ingest_gps(request: Request):
    data = await request.json()
    response = engine.process_gps(data)

    # Load existing data (dictionary) if file exists
    alerts_dict = {}
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                alerts_dict = json.load(f)
            except json.JSONDecodeError:
                alerts_dict = {}

    # Extract tourist_id from the response, use as key
    tourist_id = response.get("tourist_id")
    if tourist_id is None:
        # Handle missing tourist_id gracefully
        return {"error": "tourist_id missing in response"}

    # Store or update the data for this tourist_id
    # If you want to store multiple entries per tourist, use a list:
    if tourist_id not in alerts_dict:
        alerts_dict[tourist_id] = []

    alerts_dict[tourist_id].append(data)

    # Save updated dict back to file
    with open(LOG_FILE, "w") as f:
        json.dump(alerts_dict, f, indent=2)

    return response


@app.get("/alerts")
async def get_alerts(only_alerts: Optional[bool] = False):
    alerts = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                alerts = json.load(f)
            except json.JSONDecodeError:
                alerts = []
    if only_alerts:
        alerts = [alert for alert in alerts if alert.get("alert", False)]
    return JSONResponse(content=alerts)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
