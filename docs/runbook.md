# Runbook

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m daily_ops_agent.cli.main brief

uvicorn daily_ops_agent.api.main:app --reload
# open http://localhost:8000/brief/daily
```

## Docker

```bash
docker compose up --build
# http://localhost:8000/brief/daily
```

## Memory endpoints

- `GET /memory?limit=20`
- `POST /memory` with JSON:

```json
{"day":"2026-02-08","decision":"Paused Meta ads for SKU-001","outcome":"ROAS improved next day"}
```
