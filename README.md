# Daily Ops Agent

Autonomous **Daily Ops Brief** generator for e-commerce: aggregates read-only metrics (Shopify + Meta Ads + Google Ads), detects performance anomalies, and maintains a lightweight decision memory.

## Why this exists
A recruiter/client should be able to run this in minutes and understand:
- how data connectors are structured
- how metrics are normalized
- how alerts are generated
- how memory is persisted

## Quickstart (local)

### 1) Requirements
- Python 3.11+

### 2) Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Run demo (mock adapters)
```bash
python -m daily_ops_agent.cli brief --date yesterday
```

## Status
MVP in progress.
