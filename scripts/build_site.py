#!/usr/bin/env python3
"""Builds docs/ as a static GitHub Pages site from organisations/*.md and data/REUSE_V5_Master.csv.
Free to re-run — no API calls needed, matching the project's CSV-generation cost philosophy."""

import csv
import html
import os
import re
import shutil

import markdown

import generate_locations_json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORG_DIR = os.path.join(REPO_ROOT, "organisations")
CSV_PATH = os.path.join(REPO_ROOT, "data", "REUSE_V5_Master.csv")
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
PROFILES_DIR = os.path.join(DOCS_DIR, "organisations")

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — REUSE.IQ</title>
<meta name="description" content="{description}">
<link rel="icon" href="{favicon_path}" type="image/png">
<link rel="stylesheet" href="{css_path}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@700;800&display=swap" rel="stylesheet">
</head>
<body>
<header class="site-header">
  <a class="brand" href="{home_path}"><span class="brand-reuse">REUSE</span><span class="brand-iq">.IQ</span></a>
</header>
<main class="profile">
{body}
</main>
<footer class="site-footer">
  <p>Research-grade circular-economy organisation database. <a href="{home_path}">Back to index</a></p>
</footer>
</body>
</html>
"""

INDEX_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>REUSE.IQ</title>
<meta name="description" content="A research-grade, citable database of {count} circular-economy and reuse organisations worldwide.">
<link rel="icon" href="assets/reuse-logo.png" type="image/png">
<link rel="stylesheet" href="assets/style.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.Default.css" />
</head>
<body>
<header class="site-header">
  <div class="brand-block">
    <span class="brand"><span class="brand-reuse">REUSE</span><span class="brand-iq">.IQ</span></span>
    <p class="tagline">REUSE Foundation’s database of over 800 reuse businesses worldwide helping prevent plastic waste</p>
  </div>
</header>
<div class="banner-notice">
  <p>📋 Spot an error, or know an organisation we're missing? <a href="https://docs.google.com/forms/d/e/1FAIpQLSe_flqrEXOmmf-IfqSQGh_H-9qflTSvqqopmbcNpWj_QB9rvg/viewform">Report a correction</a> · <a href="https://docs.google.com/forms/d/e/1FAIpQLSd1e4e8IPGx8PdBmmNGUbQ0RonYZuTFBcnPsP8cJoESxbl8JA/viewform">Suggest a new organisation</a>. And if you have suggestions on how to improve this database, please share your <a href="https://docs.google.com/forms/d/e/1FAIpQLSf_8itKRYGlxBONOcUcPkZ9TVUiyH7RMpN22xXIu736N0BRrw/viewform">recommendations</a>.</p>
</div>
<main class="index">
  <div class="hero-row">
    <div class="hero-copy">
      <p class="subtitle"><b>Welcome to REUSE.IQ</b>, a global database of reuse solutions. Thank you for your interest!</p>
      <p class="subtitle">It’s currently in beta as we expand its reach and improve the quality of the data it holds - if you see an error or want to suggest a new organisation, please use the links above</p>
      <p class="subtitle">Also, we are actively talking to some organisations to prepare case studies that showcase their work and how they can prevent plastic waste. If you are interested in working with us to prepare one, please <a href="https://docs.google.com/forms/d/e/1FAIpQLSc3Zk8OCuw2pbU9d_G2XjV2rre8wgEsDIaI64cga7ApmZayXA/viewform">complete this form</a>.</p>
    </div>
    <div class="map-preview-card" id="preview-card" tabindex="0" role="button" aria-label="Open full map of reuse organisations">
      <div id="preview-map"></div>
      <div class="preview-overlay">
        <span class="preview-stat"><strong>{geocoded_count}</strong>organisations</span>
        <span class="expand-pill">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
          </svg>
          Click to expand
        </span>
      </div>
    </div>
  </div>

  <div id="summary" class="summary"></div>

  <div class="panel">
    <div class="controls">
      <div class="control">
        <label for="search">Search</label>
        <input type="search" id="search" placeholder="Name, country, category, summary…" autocomplete="off">
      </div>
      <div class="control">
        <label for="country-filter">Country</label>
        <select id="country-filter"><option value="">All countries</option></select>
      </div>
    </div>
    <div class="status-legend">
      <span class="legend-row"><span class="legend-dot status-active"></span> Blue/default — Confirmed or presumed active</span>
      <span class="legend-row"><span class="legend-dot status-warn"></span> Amber — Status uncertain or unverified</span>
      <span class="legend-row"><span class="legend-dot status-bad"></span> Red — Reported closed, inactive, or in liquidation</span>
    </div>
    <div class="actions">
      <div class="view-tabs">
        <button id="cardBtn" class="active" onclick="setView('cards')">Card view</button>
        <button id="tableBtn" onclick="setView('table')">Table view</button>
      </div>
      <button class="secondary" onclick="resetFilters()">Reset filters</button>
      <span id="result-count" class="result-count"></span>
    </div>
  </div>

  <div id="cards" class="cards"></div>

  <div id="tableWrap" class="table-wrap hidden">
    <table id="org-table">
      <thead>
        <tr>
          <th data-key="name" class="sortable">Organisation</th>
          <th data-key="country" class="sortable">Country</th>
          <th data-key="categories">Categories</th>
          <th data-key="year" class="sortable">Founded</th>
          <th data-key="status" class="sortable">Status</th>
        </tr>
      </thead>
      <tbody id="org-table-body"></tbody>
    </table>
  </div>
</main>

<div class="map-modal" id="map-modal" role="dialog" aria-modal="true" aria-label="Interactive map of reuse organisations">
  <div class="map-modal-backdrop" id="modal-backdrop"></div>
  <div class="map-modal-panel">
    <div class="modal-header">
      <h2 class="modal-title">Reuse organisations <span class="count" id="visible-count">{geocoded_count}</span></h2>
      <div class="modal-search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>
        </svg>
        <input type="text" id="map-search" placeholder="Filter by name, country or category&hellip;" />
      </div>
      <button class="modal-close" id="modal-close" aria-label="Close map">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
      </button>
    </div>
    <div class="modal-body">
      <div id="full-map"></div>
      <div class="legend">
        <div class="legend-row"><span class="legend-dot city"></span> Precise location known</div>
        <div class="legend-row"><span class="legend-dot country"></span> Country-level estimate</div>
      </div>
    </div>
  </div>
</div>

<footer class="site-footer">
  <p>Data generated from <a href="data/REUSE_V5_Master.csv">REUSE_V5_Master.csv</a>. Last built: {build_date}.</p>
  <p class="footer-note">Help us keep this database accurate and complete. Use the links above to report corrections or suggest organisations we've missed — every submission is reviewed before being added.</p>
  <p class="footer-version">Version: 1.0.02, last updated 17 August 2026</p>
</footer>
<script src="assets/data.js"></script>
<script src="assets/site.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.min.js"></script>
<script src="assets/map.js"></script>
</body>
</html>
"""

CSS = """
:root {
  color-scheme: light dark;
  --bg: #ffffff;
  --card: #f7fbfe;
  --fg: #282626;
  --muted: #66655f;
  --accent: #57c7ff;
  --accent-dark: #006699;
  --accent-bg: #e8f7ff;
  --teal: #ddf3ff;
  --amber: #fff2cc;
  --amber-fg: #735600;
  --red: #fde8e8;
  --red-fg: #9b1c1c;
  --border: #dfe6ea;
  --row-hover: #f5fbff;
  --shadow: 0 8px 24px rgba(20,30,40,.07);
  --header-bg: #000000;
  --header-fg: #ffffff;
  --ink: #16241d;
  --paper: #f6f5f0;
  --paper-raised: #ffffff;
  --line: #dad5c8;
  --forest: #2f6e51;
  --forest-dark: #1f4d38;
  --map-amber: #c17a3c;
  --amber-soft: #eadfc9;
  --mono: 'IBM Plex Mono', 'SF Mono', Consolas, monospace;
  --sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #000000;
    --card: #111214;
    --fg: #f0f1f2;
    --muted: #9a9d9f;
    --accent: #57c7ff;
    --accent-dark: #57c7ff;
    --accent-bg: #0d2733;
    --teal: #0d2733;
    --amber: #3a2f10;
    --amber-fg: #e8d290;
    --red: #3a1616;
    --red-fg: #f4a6a6;
    --border: #262a2d;
    --row-hover: #0c0d0f;
    --shadow: 0 8px 24px rgba(0,0,0,.5);
    --header-bg: #000000;
    --header-fg: #ffffff;
  }
}
:root[data-theme="dark"] {
  --bg: #000000; --card: #111214; --fg: #f0f1f2; --muted: #9a9d9f;
  --accent: #57c7ff; --accent-dark: #57c7ff; --accent-bg: #0d2733;
  --teal: #0d2733; --amber: #3a2f10; --amber-fg: #e8d290;
  --red: #3a1616; --red-fg: #f4a6a6; --border: #262a2d; --row-hover: #0c0d0f;
  --shadow: 0 8px 24px rgba(0,0,0,.5); --header-bg: #000000; --header-fg: #ffffff;
}
:root[data-theme="light"] {
  --bg: #ffffff; --card: #f7fbfe; --fg: #282626; --muted: #66655f;
  --accent: #57c7ff; --accent-dark: #006699; --accent-bg: #e8f7ff;
  --teal: #ddf3ff; --amber: #fff2cc; --amber-fg: #735600;
  --red: #fde8e8; --red-fg: #9b1c1c; --border: #dfe6ea; --row-hover: #f5fbff;
  --shadow: 0 8px 24px rgba(20,30,40,.07); --header-bg: #000000; --header-fg: #ffffff;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--fg);
  line-height: 1.55;
}
.site-header {
  padding: 2.1rem 2.2rem 1.7rem;
  background: var(--header-bg);
  color: var(--header-fg);
}
.site-header .brand {
  color: var(--header-fg);
  text-decoration: none;
  font-weight: 800;
  font-size: 1.7rem;
  letter-spacing: -0.02em;
  display: inline-flex;
  align-items: center;
  font-family: 'Poppins', var(--sans);
}
.brand-reuse { color: var(--header-fg); }
.brand-iq { color: var(--accent); }
.site-header .tagline { margin: 0.4rem 0 0; max-width: 900px; color: #d7d7d7; line-height: 1.5; }
.banner-notice {
  background: var(--accent-bg);
  border-bottom: 1px solid var(--border);
  padding: 0.7rem 2.2rem;
  text-align: center;
}
.banner-notice p { margin: 0; font-size: 0.88rem; color: var(--accent-dark); }
.banner-notice a { color: var(--accent-dark); font-weight: 700; text-decoration: underline; }
.banner-notice a:hover { text-decoration: none; }
main.index, main.profile {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem 4rem;
}
h1 { font-size: 1.6rem; margin-bottom: 0.4rem; }
.subtitle { color: var(--muted); max-width: 80ch; margin: 1.2rem 0 1.2rem; }
.subtitle a, .site-footer a { color: var(--accent-dark); font-weight: 600; }

.hero-row { display: grid; grid-template-columns: 1fr 400px; gap: 2rem; align-items: start; margin: 0.4rem 0 1.2rem; }

/* ---------- Preview map card ---------- */
.map-preview-card {
  position: relative; border-radius: 14px; overflow: hidden; border: 1px solid var(--line);
  background: var(--paper-raised); box-shadow: 0 1px 2px rgba(22,36,29,0.04); cursor: pointer;
  transition: box-shadow 0.18s ease, transform 0.18s ease;
}
.map-preview-card:hover { box-shadow: 0 6px 20px rgba(22,36,29,0.10); transform: translateY(-1px); }
.map-preview-card:focus-visible { outline: 3px solid var(--forest); outline-offset: 2px; }
#preview-map { height: 280px; width: 100%; background: #e9e6dc; }
#preview-map { pointer-events: none; }
.preview-overlay {
  position: absolute; inset: 0; display: flex; align-items: flex-end; justify-content: space-between;
  padding: 14px 16px; background: linear-gradient(180deg, rgba(22,36,29,0) 55%, rgba(22,36,29,0.55) 100%);
  pointer-events: none;
}
.preview-stat { font-family: var(--mono); font-size: 13px; color: #fff; letter-spacing: 0.02em; }
.preview-stat strong { font-size: 18px; display: block; line-height: 1.1; }
.expand-pill {
  font-family: var(--sans); font-size: 13px; font-weight: 600; color: var(--ink); background: #fff;
  padding: 8px 14px; border-radius: 999px; display: inline-flex; align-items: center; gap: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.expand-pill svg { width: 14px; height: 14px; }

/* ---------- Modal ---------- */
.map-modal { position: fixed; inset: 0; z-index: 1000; display: none; }
.map-modal.is-open { display: block; }
.map-modal-backdrop { position: absolute; inset: 0; background: rgba(16, 24, 20, 0.55); backdrop-filter: blur(2px); opacity: 0; transition: opacity 0.2s ease; }
.map-modal.is-open .map-modal-backdrop { opacity: 1; }
.map-modal-panel {
  position: absolute; inset: 20px; background: var(--paper-raised); border-radius: 16px; overflow: hidden;
  display: flex; flex-direction: column; transform: scale(0.97); opacity: 0;
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.map-modal.is-open .map-modal-panel { transform: scale(1); opacity: 1; }
@media (prefers-reduced-motion: reduce) {
  .map-modal-backdrop, .map-modal-panel, .map-preview-card { transition: none !important; }
}
.modal-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 18px; border-bottom: 1px solid var(--line); background: var(--paper-raised); }
.modal-title { font-size: 15px; font-weight: 600; margin: 0; display: flex; align-items: baseline; gap: 8px; }
.modal-title .count { font-family: var(--mono); font-size: 12px; color: var(--forest); background: var(--amber-soft); background: #e4efe8; padding: 2px 8px; border-radius: 999px; }
.modal-search { flex: 1; max-width: 320px; position: relative; }
.modal-search input { width: 100%; font-family: var(--sans); font-size: 13px; padding: 8px 12px 8px 32px; border-radius: 8px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); }
.modal-search input:focus { outline: 2px solid var(--forest); outline-offset: -1px; }
.modal-search svg { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); width: 14px; height: 14px; color: #8a8577; }
.modal-close { border: none; background: var(--paper); width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: var(--ink); flex-shrink: 0; }
.modal-close:hover { background: var(--line); }
.modal-close:focus-visible { outline: 2px solid var(--forest); }
.modal-body { flex: 1; position: relative; }
#full-map { height: 100%; width: 100%; }
.legend { position: absolute; bottom: 16px; left: 16px; z-index: 500; background: rgba(255,255,255,0.95); border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; font-size: 12px; line-height: 1.7; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
.legend-row { display: flex; align-items: center; gap: 8px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.legend-dot.city { background: var(--forest); }
.legend-dot.country { background: transparent; border: 2px solid var(--map-amber); }

/* ---------- Leaflet marker + popup skin ---------- */
.reuse-marker-city { background: var(--forest); border: 2px solid #fff; border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
.reuse-marker-country { background: transparent; border: 2px solid var(--map-amber); border-radius: 50%; }
.leaflet-popup-content-wrapper { border-radius: 10px; font-family: var(--sans); }
.popup-org { font-weight: 700; font-size: 14px; margin: 0 0 2px; }
.popup-meta { font-size: 12px; color: #55503f; margin: 0 0 8px; }
.popup-meta .sep { margin: 0 4px; opacity: 0.5; }
.popup-link { font-family: var(--mono); font-size: 11px; color: var(--forest-dark); text-decoration: none; border-bottom: 1px solid currentColor; }
.marker-cluster-reuse { background: rgba(47, 110, 81, 0.18); }
.marker-cluster-reuse div { background: var(--forest); color: #fff; font-family: var(--mono); font-weight: 600; }

.summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 1.2rem;
}
.metric {
  background: var(--card); border: 1px solid var(--border); box-shadow: var(--shadow);
  border-radius: 18px; padding: 1.1rem;
}
.metric .label { color: var(--muted); font-size: 0.8rem; }
.metric .value { font-size: 1.8rem; font-weight: 800; margin-top: 0.3rem; }
.panel {
  background: var(--card); border: 1px solid var(--border); box-shadow: var(--shadow);
  border-radius: 20px; padding: 1.1rem; margin-bottom: 1.1rem;
}
.controls {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 0.75rem;
  align-items: end;
}
.control label {
  display: block; font-size: 0.75rem; font-weight: 700; color: var(--muted);
  margin-bottom: 0.35rem; text-transform: uppercase; letter-spacing: 0.03em;
}
#search, select {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--card);
  color: var(--fg);
  font-size: 0.9rem;
}
.actions { display: flex; align-items: center; gap: 0.6rem; margin-top: 0.9rem; flex-wrap: wrap; }
button {
  border: 0; border-radius: 999px; padding: 0.55rem 0.9rem; cursor: pointer;
  background: var(--accent); color: #fff; font-weight: 700; font-size: 0.85rem;
}
button.secondary, .view-tabs button { background: var(--accent-bg); color: var(--accent-dark); }
.view-tabs { display: flex; gap: 0.5rem; }
.view-tabs button.active { background: var(--accent); color: #fff; }
.result-count { color: var(--muted); font-size: 0.85rem; margin-left: auto; white-space: nowrap; }
.status-legend { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; font-size: 0.78rem; color: var(--muted); margin: 0.7rem 0 0; }
.legend-dot.status-active { background: var(--accent-bg); border: 1px solid var(--accent-dark); }
.legend-dot.status-warn { background: var(--amber); }
.legend-dot.status-bad { background: var(--red); }

.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; }
.card {
  background: var(--card); border: 1px solid var(--border); box-shadow: var(--shadow);
  border-radius: 20px; padding: 1.1rem; display: flex; flex-direction: column; gap: 0.7rem;
  outline: 3px solid transparent; outline-offset: 2px;
  transition: outline-color 0.4s ease, background-color 0.4s ease;
}
.card.card-highlight { outline-color: var(--accent); background: var(--accent-bg); }
.card h2 { margin: 0; font-size: 1.15rem; letter-spacing: -0.01em; }
.card h2 a { color: var(--fg); text-decoration: none; }
.card h2 a:hover { color: var(--accent-dark); text-decoration: underline; }
.card .meta { display: flex; gap: 0.45rem; flex-wrap: wrap; }
.pill {
  display: inline-flex; align-items: center; border-radius: 999px;
  background: var(--accent-bg); padding: 0.25rem 0.55rem; font-size: 0.72rem;
  font-weight: 700; color: var(--accent-dark); white-space: normal;
  max-width: 100%; overflow-wrap: break-word; min-width: 0;
}
.pill.score { background: var(--teal); }
.pill.warn { background: var(--amber); color: var(--amber-fg); }
.pill.bad { background: var(--red); color: var(--red-fg); }
.card .small { font-size: 0.82rem; color: var(--muted); line-height: 1.45; }
.card .field { border-top: 1px solid var(--border); padding-top: 0.55rem; }
.card .field strong {
  display: block; font-size: 0.7rem; color: var(--muted); text-transform: uppercase;
  letter-spacing: 0.04em; margin-bottom: 0.2rem;
}
.card .tags .tag-pill { margin: 0 0.25rem 0.25rem 0; }
.card .view-link { margin-top: auto; font-weight: 700; color: var(--accent-dark); text-decoration: none; font-size: 0.85rem; }
.card .view-link:hover { text-decoration: underline; }

.tag-pill {
  display: inline-block; font-size: 0.72rem; padding: 0.12rem 0.5rem; border-radius: 999px;
  background: var(--accent-bg); color: var(--accent-dark); margin: 0 0.25rem 0.25rem 0; white-space: nowrap;
}

.table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 18px; box-shadow: var(--shadow); }
table { border-collapse: collapse; width: 100%; font-size: 0.88rem; background: var(--card); }
thead th {
  text-align: left; padding: 0.7rem 0.8rem; background: var(--header-bg); color: var(--header-fg);
  white-space: nowrap; position: sticky; top: 0;
}
th.sortable { cursor: pointer; user-select: none; }
tbody td { padding: 0.6rem 0.8rem; border-bottom: 1px solid var(--border); vertical-align: top; }
tbody tr:hover td { background: var(--row-hover); }
tbody a { color: var(--accent-dark); text-decoration: none; font-weight: 600; }
tbody a:hover { text-decoration: underline; }
.priority { font-size: 0.85rem; white-space: nowrap; }
.hidden { display: none !important; }

main.profile h1 { font-size: 1.5rem; }
main.profile { max-width: 960px; }
main.profile table { width: 100%; margin: 1rem 0; background: var(--card); }
main.profile table th, main.profile table td {
  border: 1px solid var(--border); padding: 0.5rem 0.7rem; text-align: left;
}
main.profile table th { background: var(--accent-bg); color: var(--fg); }
main.profile h2 { font-size: 1.1rem; margin-top: 1.8rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
main.profile a { color: var(--accent-dark); }
.site-footer { text-align: center; color: var(--muted); font-size: 0.85rem; padding: 2rem 1.5rem 3rem; }
.site-footer .footer-note { margin-top: 0.5rem; max-width: 60ch; margin-left: auto; margin-right: auto; }
.site-footer .footer-version { margin-top: 0.4rem; font-size: 0.75rem; opacity: 0.75; }

@media (max-width: 980px) {
  .site-header, main.index, main.profile, .banner-notice { padding-left: 1.1rem; padding-right: 1.1rem; }
  .summary { grid-template-columns: repeat(2, 1fr); }
  .controls { grid-template-columns: 1fr; }
  .cards { grid-template-columns: 1fr; }
  table { min-width: 720px; }
  .hero-row { grid-template-columns: 1fr; }
}
"""

SITE_JS = """
const state = { sortKey: 'name', sortDir: 1, view: 'cards' };

function escapeHtml(str) {
  return String(str ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
}

function uniqueSorted(values) {
  return Array.from(new Set(values.filter(Boolean))).sort();
}

function populateFilters() {
  const countrySel = document.getElementById('country-filter');
  uniqueSorted(ORGS.map(o => o.country)).forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c;
    countrySel.appendChild(opt);
  });
}

function matches(org, q, country) {
  if (country && org.country !== country) return false;
  if (!q) return true;
  const hay = (org.name + ' ' + org.country + ' ' + org.categories + ' ' + org.summary).toLowerCase();
  return hay.includes(q);
}

function getFiltered() {
  const q = document.getElementById('search').value.trim().toLowerCase();
  const country = document.getElementById('country-filter').value;
  let rows = ORGS.filter(o => matches(o, q, country));
  rows.sort((a, b) => {
    const av = (a[state.sortKey] || '').toString().toLowerCase();
    const bv = (b[state.sortKey] || '').toString().toLowerCase();
    if (av < bv) return -1 * state.sortDir;
    if (av > bv) return 1 * state.sortDir;
    return 0;
  });
  return rows;
}

function priorityClass(priority) {
  const p = String(priority || '');
  if (p.includes('Essential') || p.includes('★★★★★')) return 'pill score';
  if (p.includes('High') || p.includes('★★★★')) return 'pill score';
  if (p.includes('Low relevance') || p.includes('★')) {
    if (p.includes('Low relevance')) return 'pill bad';
    if (p.includes('★★')) return 'pill warn';
  }
  return 'pill';
}

function statusClass(status) {
  const s = String(status || '').toLowerCase();
  if (s.includes('inactive') || s.includes('closed') || s.includes('defunct') || s.includes('ceased') || s.includes('liquidation')) return 'pill bad';
  if (s.includes('uncertain') || s.includes('unclear') || s.includes('unverified')) return 'pill warn';
  return 'pill';
}

function renderSummary(rows) {
  const active = rows.filter(o => /active/i.test(o.status || '') && !/inactive/i.test(o.status || '')).length;
  const countries = new Set(rows.map(o => o.country).filter(c => c && c !== 'Not publicly available')).size;
  document.getElementById('summary').innerHTML = `
    <div class="metric"><div class="label">Organisations shown</div><div class="value">${rows.length}</div></div>
    <div class="metric"><div class="label">Confirmed active</div><div class="value">${active}</div></div>
    <div class="metric"><div class="label">Countries represented</div><div class="value">${countries}</div></div>
  `;
}

function renderCards(rows) {
  document.getElementById('cards').innerHTML = rows.map(o => `
    <article class="card" data-slug="${escapeHtml(o.slug)}">
      <div>
        <h2><a href="organisations/${o.slug}.html">${escapeHtml(o.name)}</a></h2>
        <div class="meta">
          <span class="${statusClass(o.status)}">${escapeHtml(o.status || 'Status unknown')}</span>
        </div>
      </div>
      <div class="small"><strong>${escapeHtml(o.country || 'Country unknown')}</strong>${o.year ? ' · ' + (/found/i.test(o.year) ? '' : 'Founded ') + escapeHtml(o.year) : ''}</div>
      <div class="field">
        <strong>Overview</strong>
        <span class="small">${escapeHtml(o.summary || 'Not publicly available')}</span>
      </div>
      <div class="field tags">
        <strong>Categories</strong>
        ${(o.categories || '').split(',').filter(Boolean).map(t => `<span class="tag-pill">${escapeHtml(t.trim())}</span>`).join('') || '<span class="small">Not publicly available</span>'}
      </div>
      <a class="view-link" href="organisations/${o.slug}.html">View full profile →</a>
    </article>
  `).join('');
}

function renderTable(rows) {
  const tbody = document.getElementById('org-table-body');
  tbody.innerHTML = rows.map(o => `
    <tr>
      <td><a href="organisations/${o.slug}.html">${escapeHtml(o.name)}</a></td>
      <td>${escapeHtml(o.country) || '—'}</td>
      <td>${(o.categories || '').split(',').filter(Boolean).map(t => `<span class="tag-pill">${escapeHtml(t.trim())}</span>`).join('')}</td>
      <td>${escapeHtml(o.year) || '—'}</td>
      <td><span class="${statusClass(o.status)}">${escapeHtml(o.status || '—')}</span></td>
    </tr>
  `).join('');
}

function render() {
  const rows = getFiltered();
  document.getElementById('result-count').textContent = `Showing ${rows.length} of ${ORGS.length} organisations`;
  renderSummary(rows);
  if (state.view === 'cards') renderCards(rows); else renderTable(rows);
}

function setView(view) {
  state.view = view;
  document.getElementById('cards').classList.toggle('hidden', view !== 'cards');
  document.getElementById('tableWrap').classList.toggle('hidden', view !== 'table');
  document.getElementById('cardBtn').classList.toggle('active', view === 'cards');
  document.getElementById('tableBtn').classList.toggle('active', view === 'table');
  render();
}

function resetFilters() {
  document.getElementById('search').value = '';
  document.getElementById('country-filter').value = '';
  render();
}

document.getElementById('search').addEventListener('input', render);
document.getElementById('country-filter').addEventListener('change', render);

document.querySelectorAll('th.sortable').forEach(th => {
  th.addEventListener('click', () => {
    const key = th.dataset.key;
    if (state.sortKey === key) { state.sortDir *= -1; } else { state.sortKey = key; state.sortDir = 1; }
    render();
  });
});

populateFilters();
render();
"""

MAP_JS = """
(async function () {
  const res = await fetch('assets/reuse_locations.json');
  const LOCATIONS = await res.json();

  // ---------------------------------------------------------------
  // Shared marker-building logic (used by both the preview & full map)
  // ---------------------------------------------------------------
  function makeIcon(precision) {
    const cls = precision === 'city' ? 'reuse-marker-city' : 'reuse-marker-country';
    const size = precision === 'city' ? 10 : 12;
    return L.divIcon({
      className: cls,
      iconSize: [size, size],
    });
  }

  function buildMarkers(records, { withPopups }) {
    return records.map(function (rec) {
      const marker = L.marker([rec.lat, rec.lon], { icon: makeIcon(rec.precision) });
      marker.reuseRecord = rec;
      if (withPopups) {
        marker.bindPopup(
          '<p class="popup-org">' + escapeHtml(rec.name) + '</p>' +
          '<p class="popup-meta">' + escapeHtml(rec.country) +
            '<span class="sep">&middot;</span>' + escapeHtml(rec.category) + '</p>' +
          '<a class="popup-link" href="#" onclick="focusOrgInTable(\\'' + rec.id + '\\'); return false;">View in table &rarr;</a>'
        );
      }
      return marker;
    });
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str == null ? '' : String(str);
    return div.innerHTML;
  }

  // ---------------------------------------------------------------
  // Hook this up to whatever powers your existing Table/Card view.
  // Simplest approach: set the search box's value and dispatch an
  // input event so your existing filter logic picks it up.
  // ---------------------------------------------------------------
  function focusOrgInTable(id) {
    document.getElementById('map-modal').classList.remove('is-open');
    document.body.style.overflow = '';

    if (state.view === 'table') setView('cards');

    const record = LOCATIONS.find(function (r) { return r.id === id; });
    if (!record) return;

    const searchBox = document.getElementById('search');
    searchBox.value = record.name;
    searchBox.dispatchEvent(new Event('input'));

    const orgEntry = ORGS.find(function (o) { return o.name === record.name; });
    const cardEl = orgEntry ? document.querySelector('.card[data-slug="' + orgEntry.slug + '"]') : null;
    if (!cardEl) return;

    cardEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    cardEl.classList.add('card-highlight');
    setTimeout(function () { cardEl.classList.remove('card-highlight'); }, 2000);
  }
  window.focusOrgInTable = focusOrgInTable;

  // ---------------------------------------------------------------
  // PREVIEW MAP - static-feeling teaser, no interaction, cheap to draw
  // ---------------------------------------------------------------
  const previewMap = L.map('preview-map', {
    zoomControl: false,
    dragging: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    boxZoom: false,
    keyboard: false,
    attributionControl: false,
    fadeAnimation: false,
  }).setView([15, 10], 2);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 18,
  }).addTo(previewMap);

  const previewCluster = L.markerClusterGroup({
    showCoverageOnHover: false,
    spiderfyOnMaxZoom: false,
    iconCreateFunction: clusterIcon,
  });
  previewCluster.addLayers(buildMarkers(LOCATIONS, { withPopups: false }));
  previewMap.addLayer(previewCluster);

  // ---------------------------------------------------------------
  // FULL MAP - built lazily, first time the modal opens
  // ---------------------------------------------------------------
  let fullMap = null;
  let fullClusterGroup = null;
  let allMarkers = [];

  function initFullMapIfNeeded() {
    if (fullMap) return;

    fullMap = L.map('full-map', { zoomControl: true }).setView([15, 10], 2);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap &copy; CARTO',
    }).addTo(fullMap);

    fullClusterGroup = L.markerClusterGroup({
      showCoverageOnHover: false,
      iconCreateFunction: clusterIcon,
      maxClusterRadius: 50,
    });

    allMarkers = buildMarkers(LOCATIONS, { withPopups: true });
    fullClusterGroup.addLayers(allMarkers);
    fullMap.addLayer(fullClusterGroup);
  }

  function clusterIcon(cluster) {
    const count = cluster.getChildCount();
    const size = count < 10 ? 32 : count < 50 ? 40 : 50;
    return L.divIcon({
      html: '<div style="width:' + size + 'px;height:' + size + 'px;border-radius:50%;' +
        'display:flex;align-items:center;justify-content:center;font-size:' +
        (count < 100 ? 13 : 11) + 'px;">' + count + '</div>',
      className: 'marker-cluster-reuse',
      iconSize: L.point(size, size),
    });
  }

  // ---------------------------------------------------------------
  // Modal open / close
  // ---------------------------------------------------------------
  const modal = document.getElementById('map-modal');
  const previewCard = document.getElementById('preview-card');
  const closeBtn = document.getElementById('modal-close');
  const backdrop = document.getElementById('modal-backdrop');
  const searchInput = document.getElementById('map-search');
  const visibleCount = document.getElementById('visible-count');

  function openModal() {
    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    initFullMapIfNeeded();
    // Leaflet maps created while display:none render broken - fix on open.
    setTimeout(function () { fullMap.invalidateSize(); }, 50);
    searchInput.focus();
  }

  function closeModal() {
    modal.classList.remove('is-open');
    document.body.style.overflow = '';
    previewCard.focus();
  }

  previewCard.addEventListener('click', openModal);
  previewCard.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openModal(); }
  });
  closeBtn.addEventListener('click', closeModal);
  backdrop.addEventListener('click', closeModal);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && modal.classList.contains('is-open')) closeModal();
  });

  // ---------------------------------------------------------------
  // Live search/filter inside the expanded map
  // ---------------------------------------------------------------
  searchInput.addEventListener('input', function (e) {
    const q = e.target.value.trim().toLowerCase();
    fullClusterGroup.clearLayers();

    const matches = !q ? allMarkers : allMarkers.filter(function (m) {
      const r = m.reuseRecord;
      return r.name.toLowerCase().includes(q) ||
             r.country.toLowerCase().includes(q) ||
             r.category.toLowerCase().includes(q);
    });

    fullClusterGroup.addLayers(matches);
    visibleCount.textContent = matches.length;
  });
})();
"""


def slugify_fallback(name):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
    return s


def normalize_country(raw):
    """Many 'Country' CSV cells are actually 'Country — City, Region (Address)' strings
    copied from the markdown Quick Facts 'Country / HQ' field. Strip that down to just
    the country name for filtering/display; full detail stays on the profile page."""
    c = (raw or "").strip()
    c = re.split(r"\s+[—–-]\s+", c, maxsplit=1)[0]
    c = re.sub(r"\s*\(.*$", "", c).strip()
    return c


def load_rows():
    with open(CSV_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f))


HIDDEN_MD_SECTIONS = ("REUSE Foundation Assessment", "Verification Notes")


def strip_hidden_sections(text):
    """Removes site-display-only sections (and the trailing confidence line) before
    HTML conversion. Source .md files are never modified - this only affects docs/ output."""
    for header in HIDDEN_MD_SECTIONS:
        text = re.sub(
            rf"##\s*{re.escape(header)}\s*\n.*?(?=\n##\s|\Z)",
            "",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
    text = re.sub(r"\n-{3,}\s*\nConfidence\s*—.*\Z", "\n", text, flags=re.DOTALL)
    return text


def convert_org_md_to_html(slug, name):
    md_path = os.path.join(ORG_DIR, f"{slug}.md")
    if not os.path.exists(md_path):
        return None
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    text = strip_hidden_sections(text)
    body_html = markdown.markdown(text, extensions=["tables", "fenced_code"])
    return body_html


def build_profile_pages(rows):
    os.makedirs(PROFILES_DIR, exist_ok=True)
    written = 0
    for row in rows:
        slug = row.get("GitHub slug", "").strip()
        name = row.get("Organisation", "").strip()
        if not slug:
            slug = slugify_fallback(name)
        body_html = convert_org_md_to_html(slug, name)
        if body_html is None:
            continue
        summary = row.get("Short summary", "").strip() or f"Profile of {name}, a circular-economy organisation."
        description = html.escape(summary[:280])
        page = PAGE_TEMPLATE.format(
            title=html.escape(name),
            description=description,
            css_path="../assets/style.css",
            favicon_path="../assets/reuse-logo.png",
            logo_path="../assets/reuse-logo.png",
            home_path="../index.html",
            body=body_html,
        )
        out_path = os.path.join(PROFILES_DIR, f"{slug}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page)
        written += 1
    return written


def truncate(text, max_len):
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "…"


def build_index(rows):
    orgs_js = []
    for row in rows:
        slug = row.get("GitHub slug", "").strip() or slugify_fallback(row.get("Organisation", ""))
        orgs_js.append({
            "name": row.get("Organisation", "").strip(),
            "slug": slug,
            "country": normalize_country(row.get("Country", "")),
            "categories": row.get("Tags", "").strip() or row.get("Categories", "").strip(),
            "priority": row.get("REUSE priority rating", "").strip(),
            "summary": truncate(row.get("Short summary", "") or row.get("Core model", ""), 220),
            "year": truncate(row.get("Year founded", ""), 60),
            "status": row.get("Status", "").strip(),
        })

    geocoded_count = sum(1 for r in rows if r.get("Latitude", "").strip() and r.get("Longitude", "").strip())

    import json
    data_js = "const ORGS = " + json.dumps(orgs_js, ensure_ascii=False) + ";\n"

    assets_dir = os.path.join(DOCS_DIR, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    with open(os.path.join(assets_dir, "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    with open(os.path.join(assets_dir, "site.js"), "w", encoding="utf-8") as f:
        f.write(SITE_JS)
    with open(os.path.join(assets_dir, "data.js"), "w", encoding="utf-8") as f:
        f.write(data_js)
    with open(os.path.join(assets_dir, "map.js"), "w", encoding="utf-8") as f:
        f.write(MAP_JS)

    import datetime
    build_date = datetime.date.today().isoformat()
    index_html = INDEX_TEMPLATE.format(
        count=len(rows),
        geocoded_count=geocoded_count,
        gh_repo="Martydell/REUSE-Foundation-Knowledge-Library",
        build_date=build_date,
    )
    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)


def main():
    rows = load_rows()
    os.makedirs(DOCS_DIR, exist_ok=True)
    # Copy CSV for direct download/browse
    shutil.copyfile(CSV_PATH, os.path.join(DOCS_DIR, "REUSE_V5_Master.csv"))
    # .nojekyll so GitHub Pages serves files as-is (avoids Jekyll processing conflicts)
    with open(os.path.join(DOCS_DIR, ".nojekyll"), "w") as f:
        f.write("")
    written = build_profile_pages(rows)
    build_index(rows)
    generate_locations_json.main(CSV_PATH, os.path.join(DOCS_DIR, "assets", "reuse_locations.json"))
    print(f"Wrote {written} profile pages + index.html to docs/ (from {len(rows)} CSV rows)")


if __name__ == "__main__":
    main()
