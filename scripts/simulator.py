"""Fake pump sensors: posts a reading every 2 seconds, occasionally abnormal."""

import json
import os
import random
import time
import urllib.request

TARGET = os.environ.get("TARGET_URL", "http://localhost:8000")
PUMPS = ["P-201", "P-202", "P-305"]

random.seed()  # nosec B311 — simulation only, not cryptographic

while True:
    pump = random.choice(PUMPS)
    # ~1 in 5 readings drifts into warning/critical territory
    if random.random() < 0.2:
        reading = {
            "pump_id": pump,
            "temperature_c": round(random.uniform(82, 105), 1),
            "vibration_mm_s": round(random.uniform(5, 9), 1),
            "pressure_bar": round(random.uniform(1.0, 8.0), 1),
        }
    else:
        reading = {
            "pump_id": pump,
            "temperature_c": round(random.uniform(55, 75), 1),
            "vibration_mm_s": round(random.uniform(1, 4), 1),
            "pressure_bar": round(random.uniform(5, 10), 1),
        }
    try:
        req = urllib.request.Request(
            f"{TARGET}/readings",
            data=json.dumps(reading).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:  # nosec B310 — fixed http target
            result = json.loads(resp.read())
        print(f"{pump}: {result['status'].upper():8s} {reading}")
    except Exception as exc:  # noqa: BLE001 — keep simulating even if app restarts
        print(f"{pump}: app not reachable yet ({exc})")
    time.sleep(2)
