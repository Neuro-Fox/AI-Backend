# AI-Backend: Tourist Safety Monitoring System

A FastAPI-based backend service that monitors tourist GPS data, detects anomalies, and integrates with blockchain technology for security alerts.

## Overview

This system provides real-time GPS tracking and safety monitoring for tourists through a FastAPI application with blockchain integration for immutable alert logging.

## Features

- **Real-time GPS Data Ingestion**: Collect and store tourist location data
- **Blockchain Integration**: Log safety alerts on Ethereum blockchain
- **Live Data Streaming**: Server-sent events (SSE) for real-time updates
- **Background Monitoring**: Automated anomaly detection system
- **Smart Contract Integration**: User registration and alert management

## Quick Start

### Prerequisites

- Python 3.11+
- Ethereum node access
- Environment variables configured

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirement.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Environment Variables

```env
ETH_NODE_URL=your_ethereum_node_url
SENDER_ADDRESS=your_wallet_address
PRIVATE_KEY=your_private_key
CONTRACT_ADDRESS=deployed_contract_address
```

### Running the Server

```bash
python3 backend/app.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST `/ingest`
Submit GPS data for a tourist
```json
{
  "tourist_id": "user123",
  "lat": 40.7128,
  "lon": -74.0060,
  "timestamp": "2025-09-30T12:00:00"
}
```

### GET `/data`
Retrieve all stored GPS data

### GET `/stream`
Subscribe to real-time GPS updates via Server-Sent Events

## Blockchain Features

- **User Registration**: Register tourists with travel itineraries
- **Alert System**: Automated safety alerts with location data
- **Zone Alerts**: Broadcast warnings for specific geographic areas
- **Admin Management**: Role-based access control

## Smart Contract Functions

- `registerUser()`: Register new tourist with travel details
- `Alert()`: Log safety alerts with GPS coordinates
- `sendZoneAlert()`: Broadcast area-specific warnings
- `getUserDetails()`: Retrieve tourist information

## Data Structure

GPS entries are stored in JSON format with automatic timestamping and user organization.

## Background Processing

The system runs automated monitoring every 60 seconds to check for new data and potential anomalies.

## Development

Built with:
- **FastAPI**: Modern web framework
- **Web3.py**: Ethereum blockchain interaction
- **APScheduler**: Background task scheduling
- **Pydantic**: Data validation

---

*For technical support or questions, refer to the codebase documentation.*    
