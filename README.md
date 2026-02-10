# Daily Ops Agent

Autonomous **Daily Ops Brief** generator for e-commerce: aggregates read-only metrics (Shopify + Meta Ads + Google Ads), detects performance anomalies, and maintains a lightweight decision memory.

## Why this exists
This project was built to **apply and showcase my learnings** in agentic systems and production-style engineering.

It is also inspired by real-world client needs (daily ops reporting), and serves as a reusable template to:
- structure data connectors cleanly
- normalize metrics into a single domain model
- generate anomaly/alert signals
- persist lightweight decision memory (SQLite)

## Quickstart (local)

### 1) Requirements
- Python 3.11+

### 2) Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Run demo (mock adapters)
```bash
python -m daily_ops_agent.cli.main brief
```

### 4) Run API
```bash
uvicorn daily_ops_agent.api.main:app --reload
```

Open:
- Interactive API docs (Swagger UI): **http://127.0.0.1:8000/docs**
- Daily brief endpoint: **http://127.0.0.1:8000/brief/daily**

## Docker
```bash
docker compose up --build
```

## Docs
- `docs/architecture.md`
- `docs/runbook.md`

## Status
MVP: brief + alerts + API + SQLite decision memory. Next: change detection + real adapters.
