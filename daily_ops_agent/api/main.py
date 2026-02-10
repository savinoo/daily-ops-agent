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

UI_VERSION = "v3"

app = FastAPI(title="Daily Ops Agent", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Daily Ops Agent</title>
  <style>
    :root{
      --bg:#0b1220;
      --panel:#111b2e;
      --panel2:#0f172a;
      --text:#e5e7eb;
      --muted:#94a3b8;
      --border:rgba(148,163,184,.20);
      --green:#22c55e;
      --blue:#60a5fa;
      --red:#ef4444;
      --shadow:0 10px 30px rgba(0,0,0,.35);
      --radius:16px;
    }
    *{box-sizing:border-box}
    body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;background:radial-gradient(1200px 700px at 15% 10%, rgba(96,165,250,.18), transparent 55%), radial-gradient(900px 600px at 80% 0%, rgba(34,197,94,.12), transparent 55%), var(--bg); color:var(--text)}
    a{color:var(--blue); text-decoration:none}
    a:hover{text-decoration:underline}

    .wrap{max-width:1100px;margin:0 auto;padding:28px}
    .top{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:18px}
    .title{margin:0;font-size:34px;letter-spacing:-.03em}
    .sub{margin:6px 0 0;color:var(--muted)}
    .links{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}
    .chip{border:1px solid var(--border);background:rgba(17,27,46,.65);padding:8px 10px;border-radius:999px;font-size:13px}

    .grid{display:grid;grid-template-columns:1.1fr .9fr;gap:16px}
    @media (max-width: 980px){.grid{grid-template-columns:1fr}}

    .card{background:rgba(17,27,46,.8);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow)}
    .card-h{padding:14px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;gap:12px}
    .card-b{padding:16px}
    .h2{margin:0;font-size:14px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.09em}

    .tabs{display:flex;gap:8px;flex-wrap:wrap}
    .tab{cursor:pointer;border:1px solid var(--border);background:rgba(15,23,42,.6);color:var(--text);padding:10px 12px;border-radius:12px;font-weight:600}
    .tab[aria-selected="true"]{border-color:rgba(96,165,250,.55);box-shadow:0 0 0 3px rgba(96,165,250,.15)}

    .actions{display:flex;gap:10px;flex-wrap:wrap}
    .btn{cursor:pointer;border:1px solid var(--border);background:rgba(96,165,250,.12);color:var(--text);padding:10px 12px;border-radius:12px;font-weight:700}
    .btn.primary{background:rgba(34,197,94,.18);border-color:rgba(34,197,94,.35)}
    .btn.secondary{background:rgba(148,163,184,.08)}
    .btn:disabled{opacity:.5;cursor:not-allowed}

    .alertline{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 0}
    .badge{border:1px solid var(--border);background:rgba(15,23,42,.7);padding:6px 10px;border-radius:999px;font-size:12px}
    .badge.high{border-color:rgba(239,68,68,.5);background:rgba(239,68,68,.12)}
    .badge.med{border-color:rgba(96,165,250,.5);background:rgba(96,165,250,.10)}
    .badge.low{border-color:rgba(34,197,94,.5);background:rgba(34,197,94,.10)}

    /* Markdown-ish rendering */
    #brief-md h1{font-size:20px;margin:0 0 10px}
    #brief-md h2{font-size:14px;margin:14px 0 8px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
    #brief-md ul{margin:6px 0 0 18px}
    #brief-md li{margin:6px 0}
    #brief-md code{background:rgba(96,165,250,.12);border:1px solid var(--border);padding:2px 6px;border-radius:8px}
    #brief-md strong{color:#fff}

    pre{margin:0;white-space:pre-wrap;word-break:break-word;background:rgba(15,23,42,.65);border:1px solid var(--border);padding:14px;border-radius:14px;overflow:auto;max-height:520px}

    label{display:block;font-size:12px;color:var(--muted);margin-bottom:6px}
    input,textarea{width:100%;background:rgba(15,23,42,.65);border:1px solid var(--border);color:var(--text);padding:10px 12px;border-radius:12px}
    textarea{min-height:90px;resize:vertical}
    .row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
    @media (max-width: 680px){.row2{grid-template-columns:1fr}}

    .banner{display:none;margin:10px 0 0;padding:10px 12px;border-radius:12px;border:1px solid var(--border);background:rgba(96,165,250,.10)}
    .banner.error{background:rgba(239,68,68,.12);border-color:rgba(239,68,68,.25)}
    .banner.ok{background:rgba(34,197,94,.12);border-color:rgba(34,197,94,.25)}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div>
        <h1 class="title">Daily Ops Agent <span style="font-size:12px;color:var(--muted);font-weight:600">(""" + UI_VERSION + """)</span></h1>
        <p class="sub">Daily ops brief + alerts + decision memory (mock adapters). Built as a product-style portfolio project.</p>
        <p class="sub" style="margin-top:10px;max-width:72ch">
          This app simulates an internal “Daily Ops” agent for e-commerce teams. It aggregates metrics, compares yesterday vs baseline,
          flags anomalies, stores lightweight decision memory, and snapshots landing pages to detect changes.
        </p>
      </div>
      <div class="links">
        <a class="chip" href="/docs">Swagger /docs</a>
        <a class="chip" href="/brief/daily">/brief/daily</a>
        <a class="chip" href="/changes?limit=20">/changes</a>
        <a class="chip" href="/memory?limit=20">/memory</a>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-h">
          <div class="tabs" role="tablist" aria-label="Sections">
            <button class="tab" id="tab-brief" aria-selected="true" onclick="showTab('brief')">Brief</button>
            <button class="tab" id="tab-changes" aria-selected="false" onclick="showTab('changes')">Changes</button>
            <button class="tab" id="tab-memory" aria-selected="false" onclick="showTab('memory')">Memory</button>
          </div>
          <div class="actions" id="actions"></div>
        </div>
        <div class="card-b">
          <div id="banner" class="banner"></div>

          <div id="panel-brief">
            <div style="color:var(--muted)">Generate a Daily Ops Brief (mock data) and review alerts.</div>
            <div id="alerts" class="alertline"></div>
            <div style="height:10px"></div>
            <div id="brief-md" style="display:none;background:rgba(15,23,42,.45);border:1px solid var(--border);padding:14px;border-radius:14px;max-height:520px;overflow:auto"></div>
            <pre id="brief">Click “Generate” to render the brief…</pre>
          </div>

          <div id="panel-changes" style="display:none">
            <div style="color:var(--muted)">Snapshot demo landing pages and inspect the stored hash history.</div>
            <div style="height:10px"></div>
            <pre id="changes">Click “Snapshot” or “Refresh” to load changes…</pre>
          </div>

          <div id="panel-memory" style="display:none">
            <div style="color:var(--muted)">Store decisions + outcomes to build decision memory over time.</div>
            <div style="height:10px"></div>
            <div class="row2">
              <div>
                <label>Decision</label>
                <textarea id="mem-decision" placeholder="e.g., Paused Meta ads for SKU-001"></textarea>
              </div>
              <div>
                <label>Outcome (optional)</label>
                <textarea id="mem-outcome" placeholder="e.g., ROAS improved next day"></textarea>
                <div style="height:8px"></div>
                <label>Day (optional)</label>
                <input id="mem-day" placeholder="YYYY-MM-DD" />
              </div>
            </div>
            <div style="height:10px"></div>
            <pre id="memory">Click “Load” to view memory…</pre>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-h">
          <div class="h2">Raw JSON</div>
          <div style="color:var(--muted)" id="json-label">/brief/daily</div>
        </div>
        <div class="card-b">
          <pre id="raw">Click an action to load JSON…</pre>
        </div>
      </div>
    </div>
  </div>

  <script>
    window.__dailyOpsUiLoaded = true;
    window.__dailyOpsUiVersion = '""" + UI_VERSION + """';
    const state = { tab: 'brief' };

    function setBanner(kind, msg){
      const b = document.getElementById('banner');
      if(!msg){ b.style.display='none'; b.className='banner'; b.textContent=''; return; }
      b.style.display='block';
      b.className = 'banner ' + (kind || '');
      b.textContent = msg;
    }

    function setActions(html){
      document.getElementById('actions').innerHTML = html;
    }

    function showTab(tab){
      state.tab = tab;
      document.getElementById('panel-brief').style.display = tab==='brief' ? '' : 'none';
      document.getElementById('panel-changes').style.display = tab==='changes' ? '' : 'none';
      document.getElementById('panel-memory').style.display = tab==='memory' ? '' : 'none';

      for (const t of ['brief','changes','memory']){
        document.getElementById('tab-'+t).setAttribute('aria-selected', t===tab ? 'true':'false');
      }
      setBanner(null, null);

      if (tab==='brief'){
        document.getElementById('json-label').textContent='/brief/daily';
        setActions(`
          <button class="btn primary" id="btn-gen" onclick="loadBrief()">Generate</button>
          <button class="btn secondary" onclick="openDocs()">Open /docs</button>
        `);
      } else if (tab==='changes'){
        document.getElementById('json-label').textContent='/changes';
        setActions(`
          <button class="btn primary" id="btn-snap" onclick="snapshotPages()">Snapshot</button>
          <button class="btn secondary" onclick="loadChanges()">Refresh</button>
        `);
      } else {
        document.getElementById('json-label').textContent='/memory';
        setActions(`
          <button class="btn primary" onclick="addMemory()">Add</button>
          <button class="btn secondary" onclick="loadMemory()">Load</button>
        `);
      }
    }

    function openDocs(){ window.location.href='/docs'; }

    async function api(path, method='GET', body=null){
      const raw = document.getElementById('raw');
      raw.textContent = 'Loading ' + method + ' ' + path + '…';
      setBanner(null, null);
      try{
        const res = await fetch(path, {
          method,
          headers: {'Content-Type':'application/json'},
          body: body ? JSON.stringify(body) : null,
        });
        const txt = await res.text();
        raw.textContent = txt;
        if (!res.ok){ setBanner('error', 'Request failed: ' + res.status); }
        else { setBanner('ok', 'OK'); }
        try { return JSON.parse(txt); } catch { return null; }
      } catch(e){
        raw.textContent = String(e);
        setBanner('error', String(e));
        return null;
      }
    }

    function setAlerts(alerts){
      const el=document.getElementById('alerts');
      el.innerHTML='';
      if(!alerts || alerts.length===0){
        el.innerHTML = '<span class="badge low">No alerts</span>';
        return;
      }
      for (const a of alerts){
        const sev = (a.severity||'low').toLowerCase();
        const span=document.createElement('span');
        span.className = 'badge ' + sev;
        span.textContent = (sev.toUpperCase()) + ': ' + (a.message||a.key);
        el.appendChild(span);
      }
    }

    async function loadBrief(){
      const btn=document.getElementById('btn-gen');
      if(btn){ btn.disabled=true; btn.textContent='Generating…'; }
      const data = await api('/brief/daily');
      if(btn){ btn.disabled=false; btn.textContent='Generate'; }
      if(!data) return;
      setAlerts(data.alerts);
      const md = data.brief_markdown || '';
      document.getElementById('brief').textContent = md;

      // lightweight markdown render for the vitrine (headers + bullets + bold)
      const html = md
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/^# (.*)$/gm,'<h1>$1</h1>')
        .replace(/^## (.*)$/gm,'<h2>$1</h2>')
        .replace(/^\- (.*)$/gm,'<li>$1</li>')
        .replace(/(<li>.*<\/li>)/gs,(m)=>'<ul>'+m+'</ul>')
        .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>')
        .replace(/\n\n+/g,'<div style="height:10px"></div>')
      ;
      const out = document.getElementById('brief-md');
      out.innerHTML = html;
      out.style.display = '';
    }

    async function snapshotPages(){
      const btn=document.getElementById('btn-snap');
      if(btn){ btn.disabled=true; btn.textContent='Snapshotting…'; }
      await api('/changes/snapshot','POST');
      if(btn){ btn.disabled=false; btn.textContent='Snapshot'; }
      await loadChanges();
    }

    async function loadChanges(){
      const data = await api('/changes?limit=20');
      document.getElementById('changes').textContent = JSON.stringify(data, null, 2);
    }

    async function loadMemory(){
      const data = await api('/memory?limit=20');
      document.getElementById('memory').textContent = JSON.stringify(data, null, 2);
    }

    async function addMemory(){
      const decision=document.getElementById('mem-decision').value.trim();
      const outcome=document.getElementById('mem-outcome').value.trim();
      const day=document.getElementById('mem-day').value.trim();
      const payload = {decision};
      if(outcome) payload.outcome=outcome;
      if(day) payload.day=day;
      const res = await api('/memory','POST',payload);
      if(res && res.ok){
        document.getElementById('mem-decision').value='';
        document.getElementById('mem-outcome').value='';
        document.getElementById('mem-day').value='';
        await loadMemory();
      }
    }

    // Initialize immediately (script is at end of body) + also on DOMContentLoaded for safety.
    showTab('brief');
    document.addEventListener('DOMContentLoaded', () => showTab('brief'));
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
