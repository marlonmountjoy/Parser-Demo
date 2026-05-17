from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["web"])


@router.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Seafood AI Ops Demo</title>
<style>
:root { --bg:#f4f7fb; --card:#ffffff; --ink:#172033; --muted:#64748b; --accent:#0f766e; --line:#e2e8f0; --danger:#b91c1c; --warn:#b45309; }
* { box-sizing:border-box; }
body { font-family: Arial, sans-serif; background:var(--bg); margin:0; color:var(--ink); }
.header { background:linear-gradient(135deg,#0f766e,#134e4a); color:white; padding:36px 44px; }
.header h1 { margin:0 0 8px; font-size:34px; }
.header p { margin:0; max-width:850px; opacity:.92; line-height:1.5; }
.container { max-width:1240px; margin:0 auto; padding:28px; }
.grid { display:grid; grid-template-columns:1.1fr .9fr; gap:22px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:22px; box-shadow:0 6px 22px rgba(15,23,42,.06); }
.scenarios { display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:22px; }
.scenario { background:white; border:1px solid var(--line); border-radius:14px; padding:14px; cursor:pointer; min-height:118px; }
.scenario:hover { border-color:var(--accent); box-shadow:0 4px 14px rgba(15,118,110,.15); }
.scenario h3 { margin:0 0 6px; font-size:15px; }
.scenario p { margin:0; color:var(--muted); font-size:13px; line-height:1.35; }
label { display:block; font-weight:bold; margin-top:14px; }
input, textarea { width:100%; padding:11px; border:1px solid #cbd5e1; border-radius:10px; margin-top:6px; font-size:14px; }
textarea { height:160px; }
button { border:0; border-radius:10px; padding:12px 16px; background:var(--accent); color:white; font-weight:bold; cursor:pointer; margin-top:16px; }
button.secondary { background:#334155; }
button.light { background:white; color:#334155; border:1px solid var(--line); }
.badge { display:inline-block; border-radius:999px; padding:6px 10px; font-size:12px; font-weight:bold; background:#ccfbf1; color:#115e59; }
.badge.urgent { background:#fee2e2; color:#991b1b; }
.badge.high { background:#ffedd5; color:#9a3412; }
.result { background:#f8fafc; border:1px solid var(--line); border-radius:12px; padding:14px; margin-top:12px; white-space:pre-wrap; }
.kpis { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin:14px 0; }
.kpi { background:#f8fafc; border:1px solid var(--line); border-radius:12px; padding:12px; }
.kpi .label { color:var(--muted); font-size:12px; }
.kpi .value { font-size:20px; font-weight:bold; margin-top:4px; }
.list-item { border-bottom:1px solid var(--line); padding:12px 0; }
.list-item:last-child { border-bottom:0; }
.list-item strong { display:block; margin-bottom:4px; }
.meta { color:var(--muted); font-size:13px; }
pre { overflow:auto; max-height:360px; }
.footer-links { margin-top:12px; color:var(--muted); font-size:14px; }
a { color:var(--accent); }
@media (max-width: 900px) { .grid, .scenarios { grid-template-columns:1fr; } }
</style>
</head>
<body>
<div class="header">
  <h1>Seafood AI Ops Demo</h1>
  <p>An AI-ready operations layer for seafood distributors. It keeps Gmail and QuickBooks in place, then turns messy business emails into structured, reviewable actions.</p>
</div>

<div class="container">
  <div class="scenarios" id="scenarioCards"></div>

  <div class="grid">
    <div class="card">
      <h2>Email Intake</h2>
      <p class="meta">Pick a scenario or paste your own email. The backend parses it into operational data.</p>

      <label>Sender</label>
      <input id="sender">

      <label>Subject</label>
      <input id="subject">

      <label>Email Body</label>
      <textarea id="body"></textarea>

      <button onclick="analyzeEmail()">Analyze Email</button>
      <button class="light" onclick="clearDemo()">Clear Demo Data</button>
    </div>

    <div class="card">
      <h2>Business Interpretation</h2>
      <div id="summary"><div class="result">Run an email analysis to see the business summary.</div></div>
    </div>
  </div>

  <div class="grid" style="margin-top:22px;">
    <div class="card">
      <h2>Action Queue</h2>
      <p class="meta">This is the reviewable workflow layer. Nothing auto-sends or posts to accounting.</p>
      <div id="actions"><div class="result">No actions yet.</div></div>
    </div>

    <div class="card">
      <h2>Parsed History</h2>
      <p class="meta">Every interpreted email becomes structured operational history.</p>
      <div id="history"><div class="result">No parsed emails yet.</div></div>
    </div>
  </div>

  <div class="card" style="margin-top:22px;">
    <h2>Technical Proof</h2>
    <p class="meta">This is the raw API response. Same backend is available at <a href="/docs">/docs</a>.</p>
    <pre id="rawJson" class="result"></pre>
    <div class="footer-links">
      API: <a href="/docs">Swagger docs</a> · <a href="/emails/parsed">Parsed JSON</a> · <a href="/emails/actions">Actions JSON</a>
    </div>
  </div>
</div>

<script>
let scenarios = [];

async function loadScenarios() {
  const res = await fetch("/demo/scenarios");
  scenarios = await res.json();
  const container = document.getElementById("scenarioCards");
  container.innerHTML = scenarios.map(s => `
    <div class="scenario" onclick="loadScenario('${s.id}')">
      <h3>${s.title}</h3>
      <p>${s.subtitle}</p>
      <p style="margin-top:8px;"><strong>Value:</strong> ${s.business_value}</p>
    </div>
  `).join("");
  loadScenario(scenarios[0].id);
}

function loadScenario(id) {
  const s = scenarios.find(x => x.id === id);
  sender.value = s.email.sender;
  subject.value = s.email.subject;
  body.value = s.email.body;
}

async function analyzeEmail() {
  const payload = { sender: sender.value, subject: subject.value, body: body.value };
  const res = await fetch("/emails/parse", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload) });
  const data = await res.json();
  rawJson.textContent = JSON.stringify(data, null, 2);
  renderSummary(data);
  await refreshActions();
  await refreshHistory();
}

function renderSummary(data) {
  const extracted = data.extracted || {};
  const meta = extracted._meta || {};
  const category = data.category.replace("_"," ").toUpperCase();

  let html = `
    <span class="badge">${category}</span>
    <div class="kpis">
      <div class="kpi"><div class="label">Confidence</div><div class="value">${Math.round(data.confidence * 100)}%</div></div>
      <div class="kpi"><div class="label">Parser</div><div class="value">${meta.parser_used || "n/a"}</div></div>
      <div class="kpi"><div class="label">AI Escalated</div><div class="value">${meta.ai_escalated ? "Yes" : "No"}</div></div>
    </div>
    <p><strong>Suggested action:</strong> ${extracted.suggested_action || "Review manually"}</p>
  `;

  if (data.category === "supplier_offer" && extracted.products?.length) {
    const p = extracted.products[0];
    html += `<div class="result">Supplier: ${extracted.supplier_name}
Product: ${p.species_common_name}
Form: ${p.form || "Not specified"}
Size: ${p.size_grade || "Not specified"}
Pack: ${p.pack_size || "Not specified"}
Quantity: ${p.quantity_lbs || "Unknown"} lbs
Price: ${p.price_per_lb ? "$" + p.price_per_lb + " / lb" : "Unknown"}
Location: ${p.location || "Not specified"}
Terms: ${extracted.terms || "Not specified"}</div>`;
  } else if (data.category === "customer_order" && extracted.lines?.length) {
    const l = extracted.lines[0];
    html += `<div class="result">Customer: ${extracted.customer_name}
Product: ${l.species_common_name}
Form: ${l.form || "Not specified"}
Cases: ${l.quantity_cases || "Not specified"}
Weight: ${l.quantity_lbs || "Not specified"} lbs
Requested Delivery: ${extracted.requested_delivery_date || "Not specified"}</div>`;
  } else if (data.category === "shipping_notice") {
    html += `<div class="result">Sender: ${extracted.sender_name || "Unknown"}
Carrier: ${extracted.carrier || "Unknown"}
Tracking/BOL: ${extracted.tracking_number || "Unknown"}
ETA: ${extracted.eta || "Unknown"}
Related PO: ${extracted.related_po_number || "Unknown"}</div>`;
  } else if (data.category === "complaint") {
    html += `<div class="result">Customer: ${extracted.customer_name || "Unknown"}
Issue: ${extracted.issue_type || "Unknown"}
Severity: ${extracted.severity || "needs_review"}
Product: ${extracted.product || "Unknown"}
Lot: ${extracted.lot_number || "Unknown"}
Details: ${extracted.details || ""}</div>`;
  } else {
    html += `<div class="result">${JSON.stringify(extracted, null, 2)}</div>`;
  }

  summary.innerHTML = html;
}

async function refreshActions() {
  const res = await fetch("/emails/actions");
  const items = await res.json();
  actions.innerHTML = items.length ? items.map(a => `
    <div class="list-item">
      <span class="badge ${a.priority}">${a.priority.toUpperCase()}</span>
      <strong>${a.title}</strong>
      <div class="meta">${a.detail}</div>
      <div class="meta">Status: ${a.status} · From parsed email #${a.parsed_email_id}</div>
    </div>
  `).join("") : `<div class="result">No actions yet.</div>`;
}

async function refreshHistory() {
  const res = await fetch("/emails/parsed");
  const items = await res.json();
  history.innerHTML = items.length ? items.map(e => `
    <div class="list-item">
      <strong>#${e.id} ${e.category.replace("_"," ")} — ${e.subject}</strong>
      <div class="meta">From ${e.sender} · Confidence ${Math.round(e.confidence * 100)}%</div>
    </div>
  `).join("") : `<div class="result">No parsed emails yet.</div>`;
}

async function clearDemo() {
  await fetch("/emails/clear", {method:"POST"});
  rawJson.textContent = "";
  summary.innerHTML = `<div class="result">Run an email analysis to see the business summary.</div>`;
  await refreshActions();
  await refreshHistory();
}

loadScenarios();
refreshActions();
refreshHistory();
</script>
</body>
</html>
"""
