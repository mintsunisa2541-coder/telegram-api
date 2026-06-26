import redis
import json
import time
import traceback

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

MAX_RETRY = 3
TIMEOUT = 30  # seconds

print("🚀 ZERO LOSS WORKER STARTED")

while True:
    try:
        # =========================
        # ATOMIC MOVE (NO LOSS)
        # =========================
        raw_job = r.brpoplpush(
            "queue:pending",
            "queue:processing",
            timeout=5
        )

        if not raw_job:
            continue

        job = json.loads(raw_job)
        job_id = job["id"]

        # mark start time
        r.hset("job:heartbeat", job_id, time.time())
        r.hset("job:status", job_id, "processing")

        print(f"📦 Processing {job_id}")

        # =========================
        # SIMULATE WORK
        # =========================
        if job["type"] == "post":
            print("📤", job["payload"]["text"])
            time.sleep(2)

        # =========================
        # SUCCESS
        # =========================
        r.hset("job:status", job_id, "done")
        r.lrem("queue:processing", 1, raw_job)

        print(f"✅ DONE {job_id}")

    except Exception as e:
        print("❌ ERROR:", e)
        traceback.print_exc()

        try:
            job["retry"] += 1

            if job["retry"] <= MAX_RETRY:
                print(f"🔁 RETRY {job_id}")
                r.lpush("queue:pending", json.dumps(job))
                r.hset("job:status", job_id, f"retry:{job['retry']}")

            else:
                print(f"💀 DEAD LETTER {job_id}")
                r.lpush("queue:failed", json.dumps(job))
                r.hset("job:status", job_id, "failed")

        except:
            pass