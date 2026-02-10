from __future__ import annotations

from datetime import date

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from daily_ops_agent.domain.anomalies import compare
from daily_ops_agent.domain.brief import render_brief
from daily_ops_agent.domain.memory import add_decision, list_memory
from daily_ops_agent.domain.pages import list_page_hashes, record_page_hash
from daily_ops_agent.infra.settings import settings
from daily_ops_agent.orchestration.pipeline import fetch_yesterday_and_baseline

app = FastAPI(title="Daily Ops Agent", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    # Minimal demo UI (no framework) so the project looks like a product.
    return """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Daily Ops Agent</title>
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;margin:24px;max-width:980px}
    .row{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}
    button{padding:10px 12px;border:1px solid #ddd;border-radius:10px;background:#0b1220;color:#fff;cursor:pointer}
    button.secondary{background:#fff;color:#0b1220}
    pre{background:#0b1220;color:#d1e7ff;padding:16px;border-radius:12px;overflow:auto}
    a{color:#2563eb}
    .hint{color:#555}
  </style>
</head>
<body>
  <h1>Daily Ops Agent</h1>
  <p class=\"hint\">Demo UI. For the full API, use <a href=\"/docs\">/docs</a>.</p>
  <div class=\"row\">
    <button onclick=\"run('/brief/daily')\">Generate Daily Brief</button>
    <button onclick=\"run('/changes/snapshot','POST')\">Snapshot Landing Pages</button>
    <button class=\"secondary\" onclick=\"run('/changes?limit=20')\">View Changes</button>
    <button class=\"secondary\" onclick=\"run('/memory?limit=20')\">View Memory</button>
  </div>

  <pre id=\"out\">Click a button to run an action…</pre>

  <script>
    async function run(path, method='GET'){
      const out=document.getElementById('out');
      out.textContent='Loading '+method+' '+path+'…';
      try{
        const res=await fetch(path,{method, headers:{'Content-Type':'application/json'}});
        const txt=await res.text();
        out.textContent=txt;
      }catch(e){
        out.textContent=String(e);
      }
    }
  </script>
</body>
</html>"""


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/brief/daily")
def daily_brief() -> dict:
    today = date.today()
    y, b = fetch_yesterday_and_baseline(today)
    alerts = compare(y, b)
    return {
        "date": y.day.isoformat(),
        "brief_markdown": render_brief(y, b, alerts),
        "alerts": [a.__dict__ for a in alerts],
    }


@app.get("/memory")
def memory(limit: int = 20) -> dict:
    items = list_memory(limit=limit)
    return {"items": [i.__dict__ for i in items]}


@app.post("/memory")
def memory_add(payload: dict) -> dict:
    decision = str(payload.get("decision", "")).strip()
    if not decision:
        return {"ok": False, "error": "decision is required"}

    outcome = payload.get("outcome")
    day = payload.get("day")

    new_id = add_decision(decision=decision, outcome=outcome, day=day)
    return {"ok": True, "id": new_id}


@app.post("/changes/snapshot")
def snapshot_pages() -> dict:
    urls = [u.strip() for u in settings.landing_pages.split(",") if u.strip()]
    results = []
    for url in urls:
        try:
            ph = record_page_hash(url)
            results.append({"ok": True, **ph.__dict__})
        except Exception as e:  # noqa: BLE001
            results.append({"ok": False, "url": url, "error": str(e)})
    return {"results": results}


@app.get("/changes")
def changes(url: str | None = None, limit: int = 50) -> dict:
    items = list_page_hashes(url=url, limit=limit)
    return {"items": [i.__dict__ for i in items]}
