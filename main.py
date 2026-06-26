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

@app.get("/dashboard")
def dashboard():
    pending = r.lrange("queue:pending", 0, -1)
    processing = r.lrange("queue:processing", 0, -1)
    failed = r.lrange("queue:failed", 0, -1)
    status = r.hgetall("job:status")

    return {
        "pending": len(pending),
        "processing": len(processing),
        "failed": len(failed),
        "status": status
    }