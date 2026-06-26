import redis
import json
import time
import os

r = redis.Redis.from_url(os.getenv("REDIS_URL"))

print("🚀 WORKER STARTED")

while True:
    try:
        job = r.brpoplpush("queue:pending", "queue:processing")
        job = json.loads(job)

        job_id = job["id"]
        print("📦 Processing:", job_id)

        # 👉 SET STATUS = processing (REALTIME)
        r.hset("job:status", job_id, "processing")

        # simulate work
        time.sleep(2)

        # 👉 DONE
        r.hset("job:status", job_id, "done")

        # remove from processing
        r.lrem("queue:processing", 1, json.dumps(job))

        print("✅ DONE:", job_id)

    except Exception as e:
        print("❌ ERROR:", e)
        time.sleep(2)