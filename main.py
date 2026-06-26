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

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# =========================
# 🌐 HOME DASHBOARD UI
# =========================
@app.get("/", response_class=HTMLResponse)
def dashboard_ui():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Job System Dashboard</title>
    <style>
        body {
            font-family: Arial;
            background: #0f172a;
            color: white;
            margin: 0;
            padding: 0;
        }
        .container {
            padding: 30px;
        }
        .card {
            background: #1e293b;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
        }
        .title {
            font-size: 24px;
            font-weight: bold;
        }
        .btn {
            padding: 10px 15px;
            background: #22c55e;
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
        }
        .btn:hover {
            background: #16a34a;
        }
        pre {
            background: #0b1220;
            padding: 10px;
            border-radius: 8px;
            overflow: auto;
        }
    </style>
</head>
<body>

<div class="container">

    <div class="card">
        <div class="title">🚀 Telegram Job System Dashboard</div>
        <p>Real-time system control panel</p>
    </div>

    <div class="card">
        <h3>📡 API Status</h3>
        <button class="btn" onclick="loadStatus()">Check Status</button>
        <pre id="output">Click button to load...</pre>
    </div>

</div>

<script>
async function loadStatus() {
    const res = await fetch("/dashboard");
    const data = await res.json();
    document.getElementById("output").innerText = JSON.stringify(data, null, 2);
}
</script>

</body>
</html>
"""