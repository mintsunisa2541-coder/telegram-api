import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
import redis
import json
import uuid
import time

# =========================
# CONFIG
# =========================
app = FastAPI()
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# =========================
# JOB MODEL INPUT
# =========================
class JobRequest(BaseModel):
    type: str
    text: str = None

# =========================
# CREATE JOB
# =========================
@app.post("/job")
def create_job(req: JobRequest):
    job_id = str(uuid.uuid4())

    job = {
        "id": job_id,
        "type": req.type,
        "payload": {
            "text": req.text
        },
        "retry": 0,
        "created_at": time.time()
    }

    # save status
    r.hset("job:status", job_id, "pending")

    # push to queue
    r.lpush("queue:pending", json.dumps(job))

    return {
        "status": "queued",
        "job_id": job_id
    }

# =========================
# GET JOB STATUS
# =========================
@app.get("/job/{job_id}")
def get_job(job_id: str):
    status = r.hget("job:status", job_id)

    return {
        "job_id": job_id,
        "status": status
    }

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    try:
        r.ping()
        return {"status": "ok", "redis": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import redis
import os

app = FastAPI()

r = redis.Redis.from_url(os.getenv("REDIS_URL"))

@app.get("/dashboard")
def dashboard():
    status = r.hgetall("job:status")

    # convert bytes → string
    clean = {k.decode(): v.decode() for k, v in status.items()}

    return JSONResponse({
        "total": len(clean),
        "status": clean
    })

from fastapi import FastAPI, WebSocket
import redis
import json
import os

app = FastAPI()

r = redis.Redis.from_url(os.getenv("REDIS_URL"))

# -------------------------
# 📡 WebSocket connections
# -------------------------
clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            # ส่งข้อมูลทุก 1 วินาที
            status = r.hgetall("job:status")

            clean = {
                k.decode(): v.decode()
                for k, v in status.items()
            }

            await websocket.send_text(json.dumps({
                "pending": len(clean),
                "processing": 0,
                "failed": 0,
                "status": clean
            }))

            await asyncio.sleep(1)

    except:
        clients.remove(websocket)