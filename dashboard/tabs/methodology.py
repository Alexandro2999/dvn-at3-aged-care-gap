"""Methodology / About page — data sources, formulas, caveats, team.

Standalone page (not part of the chapter arc). Routed via ?page=methodology.
"""

import streamlit as st
from tabs.utils import C


def _breadcrumb() -> str:
    """Simple breadcrumb variant for the methodology page (no chapter pill)."""
    return (
        f'<div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;'
        f'margin:0 0 14px;font-size:13px;color:{C["muted"]}">'
        f'<a href="?page=home" target="_self" '
        f'style="color:{C["muted"]};text-decoration:none;padding:3px 8px">🏠 Home</a>'
        f'<span style="color:#E5DDCB">›</span>'
        f'<span style="background:{C["navy"]};color:white;padding:3px 10px;'
        f'border-radius:8px;font-weight:700;font-size:13px">📖 Methodology</span>'
        f'</div>'
    )


def render() -> None:
    st.markdown(_breadcrumb(), unsafe_allow_html=True)
    st.markdown(
        '<div class="sec-h1">How this dashboard was built</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sec-p">Every number on this site is derived from publicly available '
        'aged-care and population datasets, joined at the SA3 grain. This page documents '
        'the data sources, formulas, and the caveats that shape every chart.</p>',
        unsafe_allow_html=True,
    )

    # ── Presentation scope ────────────────────────────────────────────────────
    st.markdown(
        f'<div style="background:#EAF0F5;border-left:5px solid {C["navy"]};'
        f'border-radius:8px;padding:14px 22px;margin:6px 0 18px;'
        f'color:{C["navy"]};font-size:17px;line-height:1.55">'
        f'<b>📅 Scope: 2023 → 2025.</b> All inputs are filtered at load time to the '
        f'3-year post-mandate window so the narrative stays focused and the time series '
        f'are comparable. Pre-2023 ABS / ACQSC data is intentionally not used — its '
        f'definitions and coverage are not consistent with the current 3-year frame.'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Interactive features legend ───────────────────────────────────────────
    st.markdown('<div class="sub-h">🎯 Interactive features</div>', unsafe_allow_html=True)
    _card = 'background:white;border:1px solid #E5DDCB;border-radius:8px;padding:12px 14px'
    _icon = 'font-size:17px;margin-bottom:4px;font-weight:700'
    _desc = f'color:{C["muted"]};font-size:14px;line-height:1.5'
    _hint = f'color:{C["teal"]};font-size:13px;font-weight:700;margin-top:6px'
    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:8px 0 18px">'
        f'<div style="{_card}">'
        f'<div style="{_icon}">🎚️ Sidebar Filter</div>'
        f'<div style="{_desc}">Pick a state or remoteness band — every chart and callout rewrites live.</div>'
        f'<div style="{_hint}">← try the left sidebar</div>'
        f'</div>'
        f'<div style="{_card}">'
        f'<div style="{_icon}">👆 Click-to-Drill</div>'
        f'<div style="{_desc}">Click any SA3 bar in Chapter 3 — the HCP-level donut updates to that region.</div>'
        f'<a href="?page=reveal" target="_self" style="{_hint};text-decoration:none;display:block">→ Go to Ch 3</a>'
        f'</div>'
        f'<div style="{_card}">'
        f'<div style="{_icon}">📖 Scrollytelling</div>'
        f'<div style="{_desc}">4-chapter detective arc: Gap → Cause → Victims → Verdict. Breadcrumb on every page.</div>'
        f'<a href="?page=map" target="_self" style="{_hint};text-decoration:none;display:block">→ Start at Ch 1</a>'
        f'</div>'
        f'<div style="{_card}">'
        f'<div style="{_icon}">🎛️ What-if Slider</div>'
        f'<div style="{_desc}">Move the RN-minutes threshold in Chapter 4 — compliance counts recompute live.</div>'
        f'<a href="?page=mandate" target="_self" style="{_hint};text-decoration:none;display:block">→ Go to Ch 4</a>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Data sources ──────────────────────────────────────────────────────────
    st.markdown('<div class="sub-h">🧭 Data sources</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="background:{C["white"]};border:1px solid {C["border"]};'
        f'border-radius:10px;padding:18px 22px;margin:8px 0 16px;'
        f'color:{C["navy"]};font-size:17px;line-height:1.65">'
        f'<table style="width:100%;border-collapse:collapse">'
        f'<thead><tr style="text-align:left;border-bottom:2px solid {C["border"]}">'
        f'<th style="padding:8px 6px;font-size:14px;text-transform:uppercase;'
        f'letter-spacing:0.05em;color:{C["muted"]}">Dataset</th>'
        f'<th style="padding:8px 6px;font-size:14px;text-transform:uppercase;'
        f'letter-spacing:0.05em;color:{C["muted"]}">Source</th>'
        f'<th style="padding:8px 6px;font-size:14px;text-transform:uppercase;'
        f'letter-spacing:0.05em;color:{C["muted"]}">Coverage</th>'
        f'<th style="padding:8px 6px;font-size:14px;text-transform:uppercase;'
        f'letter-spacing:0.05em;color:{C["muted"]}">Grain</th>'
        f'</tr></thead><tbody>'
        f'<tr><td style="padding:10px 6px"><b>Star ratings</b></td>'
        f'<td style="padding:10px 6px">ACQSC quarterly snapshots</td>'
        f'<td style="padding:10px 6px">May 2023 → Feb 2026 (12 snapshots)</td>'
        f'<td style="padding:10px 6px">Facility × Quarter</td></tr>'
        f'<tr style="background:{C["light"]}"><td style="padding:10px 6px"><b>Service supply</b></td>'
        f'<td style="padding:10px 6px">Aged Care Quality &amp; Safety Commission</td>'
        f'<td style="padding:10px 6px">2023 → 2025 (annual)</td>'
        f'<td style="padding:10px 6px">SA3 × Year</td></tr>'
        f'<tr><td style="padding:10px 6px"><b>Service users</b></td>'
        f'<td style="padding:10px 6px">GEN Aged Care (30 June snapshots)</td>'
        f'<td style="padding:10px 6px">2023 → 2025</td>'
        f'<td style="padding:10px 6px">SA3 × Year</td></tr>'
        f'<tr style="background:{C["light"]}"><td style="padding:10px 6px"><b>Population (65+)</b></td>'
        f'<td style="padding:10px 6px">ABS dataset 32350DS0005 Table 3</td>'
        f'<td style="padding:10px 6px">2023 → 2024</td>'
        f'<td style="padding:10px 6px">SA2 → SA3 aggregation</td></tr>'
        f'<tr><td style="padding:10px 6px"><b>Funding</b></td>'
        f'<td style="padding:10px 6px">ACQSC service-level funding</td>'
        f'<td style="padding:10px 6px">2023 → 2025</td>'
        f'<td style="padding:10px 6px">Facility × Year</td></tr>'
        f'</tbody></table></div>',
        unsafe_allow_html=True,
    )

    # ── Core formulas ─────────────────────────────────────────────────────────
    st.markdown('<div class="sub-h">📐 Core formulas</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="background:{C["white"]};border:1px solid {C["border"]};'
        f'border-radius:10px;padding:18px 22px;margin:8px 0 16px;'
        f'color:{C["navy"]};font-size:17px;line-height:1.65">'
        f'<table style="width:100%;border-collapse:collapse">'
        f'<thead><tr style="text-align:left;border-bottom:2px solid {C["border"]}">'
        f'<th style="padding:8px 6px;font-size:14px;text-transform:uppercase;'
        f'letter-spacing:0.05em;color:{C["muted"]}">Metric</th>'
        f'<th style="padding:8px 6px;font-size:14px;text-transform:uppercase;'
        f'letter-spacing:0.05em;color:{C["muted"]}">Formula</th>'
        f'<th style="padding:8px 6px;font-size:14px;text-transform:uppercase;'
        f'letter-spacing:0.05em;color:{C["muted"]}">Grain</th>'
        f'</tr></thead><tbody>'
        f'<tr><td style="padding:10px 6px"><b>Care Gap Index</b></td>'
        f'<td style="padding:10px 6px;font-family:Consolas,monospace;font-size:15px">'
        f'access_rate ÷ quality_score</td>'
        f'<td style="padding:10px 6px">SA3 × Year</td></tr>'
        f'<tr style="background:{C["light"]}"><td style="padding:10px 6px"><b>Residential Access Rate</b></td>'
        f'<td style="padding:10px 6px;font-family:Consolas,monospace;font-size:15px">'
        f'(total_residential ÷ pop_65_plus) × 100</td>'
        f'<td style="padding:10px 6px">SA3 × Year</td></tr>'
        f'<tr><td style="padding:10px 6px"><b>Quality Score</b></td>'
        f'<td style="padding:10px 6px;font-family:Consolas,monospace;font-size:15px">'
        f'mean(residents_exp, staffing, compliance, quality_measures)</td>'
        f'<td style="padding:10px 6px">Facility × Quarter</td></tr>'
        f'<tr style="background:{C["light"]}"><td style="padding:10px 6px"><b>Waitlist Pressure</b></td>'
        f'<td style="padding:10px 6px;font-family:Consolas,monospace;font-size:15px">'
        f'hcp_high_needs ÷ residential_places</td>'
        f'<td style="padding:10px 6px">SA3 × Year</td></tr>'
        f'<tr><td style="padding:10px 6px"><b>Beds per 1,000 elderly</b></td>'
        f'<td style="padding:10px 6px;font-family:Consolas,monospace;font-size:15px">'
        f'(residential_places ÷ pop_65_plus) × 1,000</td>'
        f'<td style="padding:10px 6px">SA3 × Year</td></tr>'
        f'</tbody></table></div>',
        unsafe_allow_html=True,
    )

    # ── Caveats ───────────────────────────────────────────────────────────────
    st.markdown('<div class="sub-h">⚠️ Caveats &amp; known limitations</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="background:#FBF6E5;border-left:5px solid {C["gold"]};'
        f'border-radius:8px;padding:16px 22px;margin:8px 0 18px;'
        f'color:{C["navy"]};font-size:17px;line-height:1.55">'
        f'<ul style="margin:0;padding-left:22px">'
        f'<li style="margin:6px 0"><b>2025 is a forecast</b>, not real data, for '
        f'<i>Care Gap Index</i> and <i>Residential Access Rate</i>. The scenario picker '
        f'(Baseline / Aggressive aging / Stagnation) controls the pop_65_plus projection.</li>'
        f'<li style="margin:6px 0"><b>SA3 10702 (Illawarra Catchment Reserve) excluded</b> '
        f'from ratio metrics — pop_65_plus = 0 (conservation land, not a data error).</li>'
        f'<li style="margin:6px 0"><b>Crisis-zone count (82 in 2024)</b> uses the full '
        f'service_users + supply universe. When you narrow the sidebar filter, the count '
        f'drops because some SA3s without quality data leave the joined master table.</li>'
        f'<li style="margin:6px 0"><b>CURF demographic data (Indigenous, NESB) is ACPR-level only</b> '
        f'and is not surfaced here — SA3 disaggregation would be misleading.</li>'
        f'<li style="margin:6px 0"><b>Negative funding values are kept</b> — they represent '
        f'clawback / reconciliation adjustments, not data errors.</li>'
        f'</ul></div>',
        unsafe_allow_html=True,
    )

    # ── Team & contact ────────────────────────────────────────────────────────
    st.markdown('<div class="sub-h">👥 Team &amp; contact</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="background:{C["white"]};border:1px solid {C["border"]};'
        f'border-radius:10px;padding:18px 22px;margin:8px 0 24px;'
        f'color:{C["navy"]};font-size:17px;line-height:1.65">'
        f'Built by <b>DVN AT3</b> for UTS MDSI — Autumn 2026.<br>'
        f'Source code: '
        f'<a href="https://github.com/Alexandro2999/dvn-at3-aged-care-gap" target="_blank" '
        f'style="color:{C["teal"]}">github.com/Alexandro2999/dvn-at3-aged-care-gap</a>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p style="text-align:center;color:{C["muted"]};font-size:14px;'
        f'margin:24px 0 8px;font-style:italic">'
        f'Data compiled from ACQSC, GEN Aged Care, and ABS · 2023–2026'
        f'</p>',
        unsafe_allow_html=True,
    )
