# PDCA — Make Daily Ops Agent a Useful App (v1)

## Objective
Turn `daily-ops-agent` from a portfolio demo into a **useful daily dashboard** that works without external credentials.

## Plan (P)
### User value (what Lucas can do daily)
- Input daily metrics (manual form)
- See dashboard with:
  - revenue, orders, AOV, CR
  - Meta/Google spend + ROAS
  - 7-day baseline comparisons + alert badges
- Track decisions/outcomes (already exists)
- Track landing page hash snapshots (already exists)

### Data modes
1) **Manual mode** (MVP) — no credentials required
2) CSV import (v2)
3) Real connectors (v3)

### MVP pages
- **Dashboard**: overview cards + alerts + small charts
- **Add day**: form to submit metrics for a specific date
- **Decisions**: existing memory UI
- **Changes**: existing changes UI

### Data model (SQLite)
Table: `daily_metrics`
- day (YYYY-MM-DD, unique)
- revenue, orders, sessions
- meta_spend, meta_revenue
- google_spend, google_revenue
- created_at

### API
- `POST /metrics` upsert by day
- `GET /metrics?days=30`
- `GET /dashboard?days=30` (returns computed baselines + alerts)

### Alerts
Compute baseline as 7-day average (excluding target day).
Trigger alerts for drops/spikes with configurable thresholds.

## Do (D)
Implement DB + endpoints + UI wiring.

## Check (C)
Manual test checklist:
- Add day → dashboard updates
- Add multiple days → baseline changes
- Alerts trigger when values are intentionally bad
- Memory add + load works
- Changes snapshot + list works

## Act (A)
Adjust thresholds + UI clarity based on test findings.
