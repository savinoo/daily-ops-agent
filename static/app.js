(() => {
  const UI = {
    tab: 'brief',
    setBanner(kind, msg) {
      const el = document.getElementById('banner');
      if (!msg) {
        el.className = 'hidden';
        el.textContent = '';
        return;
      }
      el.className = `mb-3 px-4 py-2 rounded-xl border text-sm ${kind === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-200' : kind === 'ok' ? 'bg-green-500/10 border-green-500/30 text-green-200' : 'bg-blue-500/10 border-blue-500/30 text-blue-200'}`;
      el.textContent = msg;
    },
    async api(path, method = 'GET', body = null) {
      UI.setBanner('info', `Loading ${method} ${path}…`);
      document.getElementById('jsonLabel').textContent = path;
      const rawEl = document.getElementById('rawJson');
      rawEl.textContent = `Loading ${method} ${path}…`;
      try {
        const res = await fetch(path, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: body ? JSON.stringify(body) : null,
        });
        const text = await res.text();
        rawEl.textContent = text;
        if (!res.ok) {
          UI.setBanner('error', `Request failed (${res.status})`);
          return null;
        }
        UI.setBanner('ok', 'OK');
        try {
          return JSON.parse(text);
        } catch {
          return null;
        }
      } catch (e) {
        rawEl.textContent = String(e);
        UI.setBanner('error', String(e));
        return null;
      }
    },
    setActions(html) {
      document.getElementById('actions').innerHTML = html;
    },
    showTab(tab) {
      UI.tab = tab;
      for (const t of ['brief', 'changes', 'memory']) {
        document.getElementById('panel-' + t).classList.toggle('hidden', t !== tab);
      }
      document.querySelectorAll('.tab').forEach((b) => {
        const active = b.dataset.tab === tab;
        b.className = active
          ? 'tab px-4 py-2 rounded-xl bg-panel2 border border-slate-700 font-semibold'
          : 'tab px-4 py-2 rounded-xl bg-transparent border border-slate-700/60 text-slate-300';
      });

      if (tab === 'brief') {
        UI.setActions(`
          <button id="btnGen" class="px-3 py-2 rounded-xl bg-green-500/15 border border-green-500/30 font-semibold" >Generate</button>
          <select id="selScenario" class="px-3 py-2 rounded-xl bg-slate-900/40 border border-slate-700 text-slate-200">
            <option value="steady_growth">Steady growth</option>
            <option value="cr_drop">CR drop</option>
            <option value="ad_spend_spike">Ad spend spike</option>
            <option value="revenue_crash">Revenue crash</option>
          </select>
          <button id="btnSeed" class="px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700">Seed</button>
          <a class="px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700" href="/docs">/docs</a>
        `);
        document.getElementById('btnGen').onclick = UI.loadBrief;
        document.getElementById('btnSeed').onclick = UI.seedData;
        UI.loadScenarios();
      } else if (tab === 'changes') {
        UI.setActions(`
          <button id="btnSnap" class="px-3 py-2 rounded-xl bg-green-500/15 border border-green-500/30 font-semibold">Snapshot</button>
          <button id="btnRefresh" class="px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700">Refresh</button>
        `);
        document.getElementById('btnSnap').onclick = UI.snapshot;
        document.getElementById('btnRefresh').onclick = UI.loadChanges;
      } else {
        UI.setActions(`
          <button id="btnAdd" class="px-3 py-2 rounded-xl bg-green-500/15 border border-green-500/30 font-semibold">Add</button>
          <button id="btnLoad" class="px-3 py-2 rounded-xl bg-slate-800/50 border border-slate-700">Load</button>
        `);
        document.getElementById('btnAdd').onclick = UI.addMemory;
        document.getElementById('btnLoad').onclick = UI.loadMemory;
      }

      UI.setBanner(null, null);
    },
    setAlertBadges(alerts) {
      const el = document.getElementById('alert-badges');
      el.innerHTML = '';
      if (!alerts || alerts.length === 0) {
        el.innerHTML = '<span class="px-3 py-1 rounded-full bg-green-500/10 border border-green-500/30 text-sm">No alerts</span>';
        return;
      }
      for (const a of alerts) {
        const sev = (a.severity || 'low').toLowerCase();
        const cls = sev === 'high'
          ? 'bg-red-500/10 border-red-500/30'
          : sev === 'med'
            ? 'bg-blue-500/10 border-blue-500/30'
            : 'bg-green-500/10 border-green-500/30';
        const span = document.createElement('span');
        span.className = `px-3 py-1 rounded-full border text-sm ${cls}`;
        span.textContent = `${sev.toUpperCase()}: ${a.message || a.key}`;
        el.appendChild(span);
      }
    },
    async loadBrief() {
      const btn = document.getElementById('btnGen');
      if (btn) { btn.disabled = true; btn.textContent = 'Loading…'; }
      // Prefer real dashboard when available
      const dash = await UI.api('/dashboard?days=30&baseline_days=7');
      if (dash && dash.current) {
        UI.setAlertBadges(dash.alerts);
        // Build a short brief from dashboard data
        const c = dash.current;
        const b = dash.baseline || {};
        const fmt = (n) => (n === null || n === undefined) ? '—' : n;
        const aov = c.orders ? (c.revenue / c.orders) : 0;
        const cr = c.sessions ? (c.orders / c.sessions) : 0;
        const meta_roas = c.meta_spend ? (c.meta_revenue / c.meta_spend) : 0;
        const google_roas = c.google_spend ? (c.google_revenue / c.google_spend) : 0;

        const md = `# Daily Ops Dashboard — ${c.day}\n\n## Summary\n- Revenue: **$${Number(c.revenue).toLocaleString()}** (baseline $${Number(b.revenue||0).toLocaleString()})\n- Orders: **${fmt(c.orders)}** (baseline ${fmt(b.orders)})\n- AOV: **$${aov.toFixed(2)}**\n- CR: **${(cr*100).toFixed(2)}%**\n\n## Paid Media\n- Meta spend: $${Number(c.meta_spend).toLocaleString()} | ROAS: ${meta_roas.toFixed(2)}\n- Google spend: $${Number(c.google_spend).toLocaleString()} | ROAS: ${google_roas.toFixed(2)}\n\n## Alerts\n${(dash.alerts||[]).length ? (dash.alerts.map(a=>`- [${a.severity.toUpperCase()}] ${a.message}`).join('\n')) : '- No alerts.'}\n`;
        document.getElementById('briefText').textContent = md;
      } else {
        // fallback to mock brief
        const data = await UI.api('/brief/daily');
        if (data) {
          UI.setAlertBadges(data.alerts);
          document.getElementById('briefText').textContent = data.brief_markdown || '';
        }
      }

      if (btn) { btn.disabled = false; btn.textContent = 'Generate'; }
    },
    async snapshot() {
      const btn = document.getElementById('btnSnap');
      if (btn) { btn.disabled = true; btn.textContent = 'Snapshotting…'; }
      await UI.api('/changes/snapshot', 'POST');
      if (btn) { btn.disabled = false; btn.textContent = 'Snapshot'; }
      await UI.loadChanges();
    },

    async loadScenarios() {
      // Populate scenario dropdown from backend (fallback to defaults if endpoint missing)
      const sel = document.getElementById('selScenario');
      if (!sel) return;
      const data = await UI.api('/mocks');
      if (!data?.items) return;
      sel.innerHTML = '';
      for (const s of data.items) {
        const opt = document.createElement('option');
        opt.value = s.key;
        opt.textContent = s.title;
        sel.appendChild(opt);
      }
    },

    async seedData() {
      const sel = document.getElementById('selScenario');
      const scenario = sel?.value || 'steady_growth';
      const btn = document.getElementById('btnSeed');
      if (btn) { btn.disabled = true; btn.textContent = 'Seeding…'; }
      const res = await UI.api(`/mocks/seed?scenario=${encodeURIComponent(scenario)}&days=8`, 'POST');
      if (btn) { btn.disabled = false; btn.textContent = 'Seed'; }
      if (res?.ok) UI.setBanner('ok', `Seeded scenario: ${scenario}. Click Generate.`);
    },
    async loadChanges() {
      const data = await UI.api('/changes?limit=20');
      const tbody = document.getElementById('changesRows');
      tbody.innerHTML = '';
      const items = data?.items || [];
      for (const it of items) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="p-3 text-slate-200 break-all">${it.url}</td>
          <td class="p-3 text-slate-400 whitespace-nowrap">${it.created_at}</td>
          <td class="p-3 font-mono text-slate-300">${String(it.content_hash).slice(0,12)}…</td>
        `;
        tbody.appendChild(tr);
      }
      if (items.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td class="p-3 text-slate-400" colspan="3">No snapshots yet. Click Snapshot.</td>';
        tbody.appendChild(tr);
      }
    },
    async loadMemory() {
      const data = await UI.api('/memory?limit=20');
      document.getElementById('memoryText').textContent = JSON.stringify(data, null, 2);
    },
    async addMemory() {
      const decision = document.getElementById('memDecision').value.trim();
      const outcome = document.getElementById('memOutcome').value.trim();
      const day = document.getElementById('memDay').value.trim();
      if (!decision) {
        UI.setBanner('error', 'Decision is required');
        return;
      }
      const payload = { decision };
      if (outcome) payload.outcome = outcome;
      if (day) payload.day = day;
      const res = await UI.api('/memory', 'POST', payload);
      if (res && res.ok) {
        document.getElementById('memDecision').value = '';
        document.getElementById('memOutcome').value = '';
        document.getElementById('memDay').value = '';
        await UI.loadMemory();
      }
    },
  };

  document.querySelectorAll('.tab').forEach((b) => b.addEventListener('click', () => UI.showTab(b.dataset.tab)));
  UI.showTab('brief');
})();
