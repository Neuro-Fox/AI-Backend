# backend/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
import os
from web3 import Web3
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
import asyncio


# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ETH_NODE_URL = os.getenv("ETH_NODE_URL")
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# OpenAI client

client = OpenAI(api_key=OPENAI_API_KEY)

# Web3 setup
w3 = Web3(Web3.HTTPProvider(ETH_NODE_URL))

# Replace this with your actual contract ABI
CONTRACT_ABI = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "address",
				"name": "userAddress",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "homeAddress",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "phoneNumber",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "aadhar",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "passport",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "alertMessage",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "int256",
				"name": "latitude",
				"type": "int256"
			},
			{
				"indexed": False,
				"internalType": "int256",
				"name": "longitude",
				"type": "int256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "AlertEvent",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "address",
				"name": "userAddress",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "UserExpired",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "address",
				"name": "userAddress",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "UserRegistered",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_alertMessage",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "_userAddress",
				"type": "address"
			},
			{
				"internalType": "int256",
				"name": "_latitude",
				"type": "int256"
			},
			{
				"internalType": "int256",
				"name": "_longitude",
				"type": "int256"
			}
		],
		"name": "Alert",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_admin",
				"type": "address"
			}
		],
		"name": "addAdmin",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_userAddress",
				"type": "address"
			}
		],
		"name": "expireUser",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getAllRegisteredUsers",
		"outputs": [
			{
				"internalType": "address[]",
				"name": "",
				"type": "address[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_userAddress",
				"type": "address"
			}
		],
		"name": "getUserDetails",
		"outputs": [
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "homeAddress",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "email",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "phoneNumber",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "aadhar",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "passport",
				"type": "string"
			},
			{
				"internalType": "bool",
				"name": "isRegistered",
				"type": "bool"
			},
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "day",
						"type": "uint256"
					},
					{
						"components": [
							{
								"internalType": "string",
								"name": "longitude",
								"type": "string"
							},
							{
								"internalType": "string",
								"name": "latitude",
								"type": "string"
							},
							{
								"internalType": "string",
								"name": "Location_name",
								"type": "string"
							}
						],
						"internalType": "struct UserRegistry.Location[]",
						"name": "locations",
						"type": "tuple[]"
					}
				],
				"internalType": "struct UserRegistry.TravelDetail[]",
				"name": "itinerary",
				"type": "tuple[]"
			},
			{
				"internalType": "uint256",
				"name": "registrationTime",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_name",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_homeAddress",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_email",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_phoneNumber",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_aadhar",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_passport",
				"type": "string"
			},
			{
				"internalType": "uint256[]",
				"name": "_days",
				"type": "uint256[]"
			},
			{
				"internalType": "string[][]",
				"name": "_longitudes",
				"type": "string[][]"
			},
			{
				"internalType": "string[][]",
				"name": "_latitudes",
				"type": "string[][]"
			},
			{
				"internalType": "string[][]",
				"name": "_locationNames",
				"type": "string[][]"
			}
		],
		"name": "registerUser",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_admin",
				"type": "address"
			}
		],
		"name": "removeAdmin",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]  # keep the ABI JSON here

EVENT_QUEUE = []

async def event_generator():
    """
    SSE generator: always yields the latest snapshot of all users
    """
    last_sent = None
    while True:
        if LAST_INPUTS and LAST_INPUTS != last_sent:
            data = dict(LAST_INPUTS)  # copy current state
            last_sent = data
            yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(1)

# File to store GPS data
DATA_LOG_FILE = "logs/data.json"
os.makedirs("logs", exist_ok=True)

# Pydantic Model
class GPSData(BaseModel):
    tourist_id: str
    lat: float
    lon: float
    timestamp: str  # ISO format

# FastAPI app
app = FastAPI()

# Helpers
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_json(path, content):
    with open(path, "w") as f:
        json.dump(content, f, indent=2)

def send_anomaly_to_blockchain(anomaly_detail, user_address, lat, lon):
    """
    Calls the `Alert` function on the deployed smart contract
    to log the anomaly on-chain.
    """
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    tx = contract.functions.Alert(
        anomaly_detail,
        user_address,
        int(lat * 1e6),
        int(lon * 1e6)
    ).buildTransaction({
        'from': SENDER_ADDRESS,
        'nonce': w3.eth.getTransactionCount(SENDER_ADDRESS),
        'gas': 300000,
        'gasPrice': w3.toWei('50', 'gwei')
    })

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(f"[Blockchain] Alert sent: {tx_hash.hex()}")
    return tx_hash.hex()

# GPT-based anomaly detection
def detect_anomaly_with_gpt(entry):
    """
    Sends GPS entry to GPT for anomaly detection.
    Returns a string describing the anomaly or None.
    """
    prompt = f"""
    You are a geo-anomaly detection assistant. Evaluate the following GPS entry for any anomalous or suspicious activity.
    Provide a detailed description of any anomalies detected. If nothing suspicious, return 'None'.

    GPS Data:
    tourist_id: {entry['tourist_id']}
    lat: {entry['lat']}
    lon: {entry['lon']}
    timestamp: {entry['timestamp']}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        anomaly_detail = response.choices[0].message.content.strip()
        if anomaly_detail.lower() == "none":
            return None
        return anomaly_detail
    except Exception as e:
        print(f"[GPT ERROR] {e}")
        return None

# Background Scheduler
last_checked = {}

def monitor_json_file():
    global last_checked
    data = load_json(DATA_LOG_FILE)
    for tourist_id, entries in data.items():
        last_ts = last_checked.get(tourist_id)
        for entry in entries:
            ts = datetime.fromisoformat(entry["timestamp"])
            if last_ts and ts <= last_ts:
                continue

            anomaly_detail = detect_anomaly_with_gpt(entry)
            if anomaly_detail:
                send_anomaly_to_blockchain(
                    anomaly_detail=anomaly_detail,
                    user_address=tourist_id,
                    lat=entry["lat"],
                    lon=entry["lon"]
                )
            print(anomaly_detail)

        if entries:
            last_checked[tourist_id] = datetime.fromisoformat(entries[-1]["timestamp"])

@app.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(monitor_json_file, "interval", seconds=60)  
    scheduler.start()


# Store latest snapshot per user
LAST_INPUTS = {}

# API Route: Ingest GPS
@app.post("/ingest")
async def ingest_gps(data: GPSData):
    all_data = load_json(DATA_LOG_FILE)
    if data.tourist_id not in all_data:
        all_data[data.tourist_id] = []

    entry = {
        "lat": data.lat,
        "lon": data.lon,
        "timestamp": data.timestamp,
        "tourist_id": data.tourist_id
    }

    all_data[data.tourist_id].append(entry)
    save_json(DATA_LOG_FILE, all_data)

    # Update last snapshot
    LAST_INPUTS[data.tourist_id] = entry

    return {"status": "success", "message": "GPS data logged", "data": entry}

# API Route: Get all data
@app.get("/data")
async def get_data():
    return load_json(DATA_LOG_FILE)

@app.get("/stream")
async def stream():
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
