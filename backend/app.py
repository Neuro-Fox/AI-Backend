from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/ingest")
async def ingest_gps(request: Request):
    data = await request.json()
    return {"status": "received", "data": data}

@app.get("/dashboard")
async def get_dashboard():
    return {"message": "Dashboard data placeholder"}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
