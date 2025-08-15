async function fetchJSON(url) {
  const r = await fetch(url, { cache: "no-store" });
  if (!r.ok) throw new Error("HTTP " + r.status);
  return await r.json();
}

function pctClass(v) { return v >= 0 ? "green" : "red"; }

function relVolumeDots(rv) {
  const dots = [];
  const value = Math.max(0, Math.min(10, Math.round((rv || 0) * 2)));
  for (let i = 0; i < 10; i++) dots.push(`<div class="dot ${i < value ? "on" : ""}"></div>`);
  return dots.join("");
}

function indicatorBadge(name, ok) {
  return `<div class="label ${ok ? "on" : ""}">${name}</div>`;
}

function cardHTML(row) {
  const pct = (row.changed_pct || 0).toFixed(2);
  const rsi1h = row.rsi_1h;
  const rsi15 = row.rsi_15m;
  const macd15 = row.macd_15m;

  return `
  <div class="card">
    <div class="row">
      <div class="sym">${row.symbol}</div>
      <div class="badge">Corr. ${row.corr_btc == null ? "—" : row.corr_btc.toFixed(2)}</div>
    </div>
    <div class="row">
      <div class="pct ${pctClass(parseFloat(pct))}">${pct}%</div>
    </div>
    <div class="labels">
      ${indicatorBadge("EMA 200", row.price && row.ema200 ? row.price > row.ema200 : false)}
      ${indicatorBadge("RSI 1h", rsi1h ? rsi1h > 50 : false)}
      ${indicatorBadge("RSI 15m", rsi15 ? rsi15 > 50 : false)}
      ${indicatorBadge("MACD 15m", macd15 ? macd15 > 0 : false)}
    </div>
    <div class="footer">Rel. Volume</div>
    <div class="meter">${relVolumeDots(row.rel_volume || 0)}</div>
  </div>`;
}

// ---- Last update (global badge) ----
function setLastUpdate(data) {
  if (!Array.isArray(data) || data.length === 0) return;
  let maxTs = 0;
  for (const x of data) {
    const t = new Date(x.created_at).getTime(); // ISO string
    if (!isNaN(t) && t > maxTs) maxTs = t;
  }
  const el = document.getElementById("last-update");
  if (el && maxTs > 0) {
    const d = new Date(maxTs);
    el.textContent = "Last update " + d.toLocaleTimeString();
  }
}

async function render() {
  try {
    const data = await fetchJSON("/api/signals?limit=100");
    const wrap = document.getElementById("cards");
    wrap.innerHTML = data.map(cardHTML).join("");
    setLastUpdate(data);
  } catch (e) {
    console.error("Failed to load", e);
  }
}

render();
setInterval(render, 15000);
