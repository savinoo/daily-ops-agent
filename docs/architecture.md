# Architecture

## Overview
`daily-ops-agent` is an opinionated template for a **Daily Ops Brief** automation:

1. **Ingest** read-only metrics from sources (Shopify, Meta Ads, Google Ads)
2. **Normalize** into a single `DailyMetrics` domain object
3. **Compare** yesterday vs baseline (7d) and trigger alerts
4. **Persist** decisions/outcomes as lightweight memory (SQLite)
5. **Generate** a Markdown brief

## Modules
- `adapters/` — external integrations (real + mock)
- `domain/` — pure business logic (metrics, anomalies, brief)
- `orchestration/` — pipeline wiring, schedules
- `infra/` — settings, db, logging
- `api/` — FastAPI endpoints
- `cli/` — CLI entrypoints

## Data flow
```
Sources -> adapters -> domain (DailyMetrics)
                     -> domain (anomalies)
                     -> infra (memory)
                     -> domain (brief Markdown)
                     -> api/cli output
```

## Security
- Public repo ships with mock adapters + `.env.example`
- Real connectors must be enabled via env flags and must never commit secrets
