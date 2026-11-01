"""Maakt index.html (voor GitHub Pages) uit dashboard/index.html.

dashboard/index.html is de pagina van het Claude-dashboard en gebruikt de
`dash`-functies van dat dashboard. Deze build zet er een kleine vervanger
van `dash` omheen die de CSV uit data/ leest, zodat dezelfde pagina ook
los op GitHub Pages werkt.

Gebruik:  python scripts/bouw_pagina.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSV = "data/bison_diensten_2026-2126.csv"

KOP = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Bison feestdagenrooster</title>
<meta name="description" content="Wie van de Bison werkt er met kerst en oud en nieuw, en is dat eerlijk verdeeld?">
<style>
:root {
  --color-bg: #f6f7f9; --color-panel: #ffffff; --color-fg: #1b1f27; --color-fg-muted: #5b6372;
  --color-border-line: #e1e4ea; --color-ok: #1f7a4d; --color-warn: #a35f00; --color-bad: #b42318;
  --cds-surface-popover: #ffffff; --cds-border: #d5d9e0; --cds-text-secondary: #5b6372;
  --cds-shadow-popover: 0 4px 16px rgba(20, 30, 50, .14);
  --cds-chart-grid: #eceef2; --cds-chart-axis: #c4c9d2; --cds-chart-reference: #1b1f27; --cds-chart-muted: #c4c9d2;
  --font-anthropic-sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-anthropic-serif: Georgia, "Times New Roman", serif;
  --cds-font-size-caption: 12px; --cds-font-size-body: 14px; --cds-font-size-heading: 16px; --cds-font-size-title: 26px;
  --cds-font-weight-medium: 600;
  --cds-gap-xs: 4px; --cds-gap-sm: 8px; --cds-gap-md: 12px; --cds-gap-lg: 20px; --cds-gap-xl: 32px;
  --cds-pad-xs: 4px; --cds-pad-sm: 8px; --cds-pad-md: 12px; --cds-pad-lg: 16px; --cds-pad-xl: 24px;
  --cds-radius: 8px; --cds-dur-slow: .3s; --cds-ease-out: cubic-bezier(.2, .8, .2, 1);
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #12151b; --color-panel: #1b1f27; --color-fg: #e8eaee; --color-fg-muted: #9aa3b2;
    --color-border-line: #2c323d; --cds-surface-popover: #232833; --cds-border: #353c48; --cds-text-secondary: #9aa3b2;
    --cds-shadow-popover: 0 4px 16px rgba(0, 0, 0, .5);
    --cds-chart-grid: #262b35; --cds-chart-axis: #3a414d; --cds-chart-reference: #e8eaee; --cds-chart-muted: #3a414d;
    color-scheme: dark;
  }
}
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--color-bg); color: var(--color-fg); font-family: var(--font-anthropic-sans); font-size: 14px;
  padding-top: env(safe-area-inset-top, 0px); padding-bottom: max(24px, env(safe-area-inset-bottom, 0px)); }
#dash-root { --dash-gutter: 12px; padding-left: max(var(--dash-gutter), env(safe-area-inset-left, 0px));
  padding-right: max(var(--dash-gutter), env(safe-area-inset-right, 0px)); padding-block: 16px; }
.dash-skeleton:empty, .dash-skeleton { color: transparent; }
.dash-skeleton { background: linear-gradient(90deg, var(--color-border-line), var(--color-panel), var(--color-border-line));
  background-size: 200% 100%; border-radius: 4px; animation: dash-sk 1.4s linear infinite; }
@keyframes dash-sk { to { background-position: -200% 0; } }
.bx-bron { font-size: 12px; color: var(--color-fg-muted); text-align: center; margin: 24px 0 0; }
.bx-bron a { color: inherit; }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>
// Kleine vervanger van de dash-functies van het Claude-dashboard.
(() => {
  const CSV = "%CSV%";
  const sources = {};   // id -> {status, data, columns}
  const calcs = {};     // id -> {inputs, fn}
  const draws = {};     // name -> fn
  const listeners = [];
  const st = (id) => sources[id] || { status: 'loading', data: [], columns: [] };
  const runCalcs = () => {
    let changed = true;
    while (changed) {
      changed = false;
      for (const [id, c] of Object.entries(calcs)) {
        if (sources[id]) continue;
        const ins = c.inputs.map(st);
        if (ins.every((s) => s.status === 'ok')) {
          try { sources[id] = { status: 'ok', data: c.fn(...ins.map((s) => s.data)), columns: [] }; }
          catch (e) { console.error(e); sources[id] = { status: 'error', data: [], columns: [], message: String(e) }; }
          changed = true;
        } else if (ins.some((s) => s.status === 'error')) {
          sources[id] = { status: 'error', data: [], columns: [] }; changed = true;
        }
      }
    }
  };
  const runDraw = (name) => document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => {
    try { draws[name](el); } catch (e) { console.error(e); }
  });
  const all = () => { listeners.forEach((f) => { try { f(); } catch (e) { console.error(e); } }); Object.keys(draws).forEach(runDraw); };
  window.dash = {
    colors: ['#3b6fd8', '#8a4fd1', '#e0912f', '#1f9e89', '#d6457a', '#6b7a8f', '#b5a22c', '#4aa3c8'],
    data: (id) => ({ ...st(id), get rows() { return this.data; } }),
    calc: (id, o) => { calcs[id] = o; },
    loader: () => {},
    onData: (fn) => { listeners.push(fn); try { fn(); } catch (e) { console.error(e); } },
    draw: (name, fn) => { if (fn) { draws[name] = typeof fn === 'function' ? fn : fn.update; } else if (draws[name]) runDraw(name); },
    params: () => ({}), setParams: () => {}, resetParams: () => {}, setLink: () => {}, refresh: () => {},
  };
  const load = () => fetch(CSV).then((r) => { if (!r.ok) throw new Error(r.status); return r.text(); }).then((t) => {
    const rows = d3.csvParse(t);
    sources.diensten = { status: 'ok', data: rows, columns: rows.columns };
  }).catch((e) => { console.error(e); sources.diensten = { status: 'error', data: [], columns: [] }; })
    .then(() => { runCalcs(); all(); });
  document.addEventListener('DOMContentLoaded', () => { all(); load(); });
  let w = window.innerWidth;
  window.addEventListener('resize', () => { if (window.innerWidth !== w) { w = window.innerWidth; all(); } });
})();
</script>
</head>
<body>
<div id="dash-root">
"""

VOET = """
<p class="bx-bron">Bron: <a href="https://github.com/hermanvandenberg/Bison-Feestdagenrooster">Bison-Feestdagenrooster</a> · berekend uit het rooster van 2027</p>
</div>
</body>
</html>
"""


def main():
    inhoud = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
    (ROOT / "index.html").write_text(KOP.replace("%CSV%", CSV) + inhoud + VOET, encoding="utf-8")
    print("index.html geschreven")


if __name__ == "__main__":
    main()
