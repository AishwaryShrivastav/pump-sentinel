"""Pump Sentinel — pump health monitoring API.

Runs locally with uvicorn, in Docker, and on AWS Lambda (via Mangum).
"""

import json
import os
import time

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from mangum import Mangum
from pydantic import BaseModel, Field

from app import __version__
from app.anomaly import check_reading

app = FastAPI(title="Pump Sentinel", version=__version__)

# In-memory history — resets on cold start; fine for a demo,
# and a good talking point about stateless deploys.
_history: list[dict] = []

ACCENT = "#3fb950"  # green — shipped by the fixed pipeline


class Reading(BaseModel):
    pump_id: str = Field(examples=["P-201"])
    temperature_c: float = Field(examples=[72.5])
    vibration_mm_s: float = Field(examples=[3.1])
    pressure_bar: float = Field(examples=[8.4])


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    rows = "".join(
        f"<tr><td>{r['pump_id']}</td><td>{r['temperature_c']}</td>"
        f"<td>{r['vibration_mm_s']}</td><td>{r['pressure_bar']}</td>"
        f"<td class='{r['status']}'>{r['status'].upper()}</td></tr>"
        for r in reversed(_history[-10:])
    )
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Pump Sentinel</title>
<style>
  body {{ font-family: -apple-system, 'Segoe UI', sans-serif; background: #0d1117;
         color: #e6edf3; display: flex; flex-direction: column; align-items: center;
         padding-top: 8vh; }}
  .chip {{ background: {ACCENT}; color: #0d1117; font-weight: 700; border-radius: 999px;
          padding: 6px 18px; font-size: 1.1rem; }}
  h1 {{ font-size: 3rem; margin: 0.4em 0 0.2em; letter-spacing: 0.04em; }}
  p {{ color: #8b949e; }}
  table {{ border-collapse: collapse; margin-top: 2em; }}
  td, th {{ padding: 8px 18px; border-bottom: 1px solid #21262d; }}
  .ok {{ color: #3fb950; }} .warning {{ color: #d29922; }} .critical {{ color: #f85149; }}
</style></head>
<body>
  <h1>PUMP SENTINEL</h1>
  <span class="chip">v{__version__}</span>
  <p>Deployed automatically by GitHub Actions &middot; running on {runtime_name()}</p>
  <table><tr><th>Pump</th><th>Temp °C</th><th>Vib mm/s</th><th>Press bar</th><th>Status</th></tr>
  {rows or "<tr><td colspan='5'>no readings yet — POST to /readings</td></tr>"}</table>
</body></html>"""


@app.get("/health")
def health() -> dict:
    return {"status": "up", "version": __version__}


@app.post("/readings")
def submit_reading(reading: Reading) -> dict:
    result = check_reading(reading.temperature_c, reading.vibration_mm_s, reading.pressure_bar)
    record = {**reading.model_dump(), **result, "ts": time.time()}
    _history.append(record)
    # Structured log of every prediction — version one of a monitoring system.
    print(json.dumps({"event": "reading", **record}))
    return result


@app.get("/readings")
def list_readings() -> list[dict]:
    return _history[-50:]


def runtime_name() -> str:
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "AWS Lambda"
    if os.path.exists("/.dockerenv"):
        return "Docker"
    return "local machine"


handler = Mangum(app)
