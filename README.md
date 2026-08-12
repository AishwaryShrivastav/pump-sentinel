# Pump Sentinel

A small pump-health monitoring API used as a teaching demo for CI/CD, Docker,
and AI-assisted engineering. Refinery-flavoured, deliberately simple.

**Live:** deployed automatically to AWS Lambda by GitHub Actions on every push
to `main` that passes lint, tests, and a security scan.

## What it does

- `POST /readings` — submit a pump sensor reading (temperature, vibration, pressure);
  gets classified `ok` / `warning` / `critical` against ISO-10816-flavoured thresholds
- `GET /` — dashboard showing version and recent readings
- `GET /health` — health check used by the pipeline's smoke test
- `GET /docs` — interactive API docs (FastAPI gives this for free)

## Run it

```bash
# Local (needs Python 3.12+)
pip install -r requirements-dev.txt
uvicorn app.main:app --reload

# Tests + lint + security scan — the same checks CI runs
ruff check . && pytest && bandit -r app -ll

# Docker — no Python needed on the machine
docker build -t pump-sentinel .
docker run -p 8000:8000 pump-sentinel

# Docker Compose — app + a fake sensor feed
docker compose up
```

## The pipeline

`.github/workflows/ci.yml` — cheap checks first, expensive checks later:

```
push → lint (ruff) → tests (pytest) → security (bandit) → deploy (Lambda) → smoke test
```

Deploys only happen from `main`, with credentials that can update exactly one
Lambda function and nothing else.
