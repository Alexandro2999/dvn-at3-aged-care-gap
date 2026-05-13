"""Chapter 5 — The Forecast.

What-if scenario for 2025: only pop_65_plus is projected (ABS unreleased).
Supply, quality, and demand use real 2025 data. Three scenarios:
  - Baseline (per-state CAGR 2019→2024)
  - Aggressive aging (+4%/yr)
  - Stagnation (0%/yr)
Recomputes care_gap_index, access_rate, beds_per_1k for 2025.
waitlist_pressure is real 2025 (does not depend on pop).
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from tabs.utils import C, theme, SCENARIO_GROWTH_RATES, build_master_2025

# (col, label, scale, higher_is_better)
_PROJ_METRICS = {
    'Care Gap Index':           ('care_gap_index', [[0, '#E3F1FA'], [0.4, '#4A7FC1'], [1, '#1B3F6E']], False),
    'Residential Access Rate':  ('access_rate',    [[0, '#F0FFF0'], [0.5, '#4CAF50'], [1, '#1B5E20']], True),
    'Beds per 1,000 elderly':   ('beds_per_1k',    [[0, '#E3F1FA'], [0.5, '#4A7FC1'], [1, '#1B3F6E']], True),
}


def render(master, supply, service_users, ratings, population, gdf) -> None:
    st.markdown('<div class="sec-h1">Chapter 5 — The Forecast</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sec-p">If the trend continues, what does 2025 look like? '
        'Only <b>pop_65_plus</b> is projected (ABS data unreleased for 2025). '
        'Supply, quality, and home-care demand all use real 2025 data.</p>',
        unsafe_allow_html=True,
    )

    # ── Controls ──────────────────────────────────────────────────────────────
    c1, c2 = st.columns([2, 2])
    with c1:
        scenario = st.radio(
            "**Population scenario**",
            options=list(SCENARIO_GROWTH_RATES.keys()),
            index=0,
            horizontal=False,
            help="Baseline = per-state CAGR 2019→2024 (ABS trend); the other two are hypothetical bounds.",
        )
    with c2:
        metric_label = st.selectbox(
            "**Projected metric**",
            options=list(_PROJ_METRICS.keys()),
            index=0,
            help="Waitlist Pressure uses real 2025 data and is not affected by population scenario.",
        )

    col_c, cscale, higher_is_better = _PROJ_METRICS[metric_label]

    st.info(
        f"**Scenario: {scenario}** — supply held at real 2025 levels; pop 65+ projected per scenario. "
        f"Quality, residential users, and HCP demand all use real 2025 data."
    )

    # ── Build 2025 frame ──────────────────────────────────────────────────────
    df25 = build_master_2025(master, supply, service_users, ratings, population, scenario)
    df25 = df25.dropna(subset=[col_c])

    # 2024 baseline frame
    df24 = master[master['year'] == 2024][['sa3_code', 'sa3_name', 'state', 'mmm_code', col_c]].copy()

    if df24.empty or df25.empty:
        st.warning("Not enough data to render 2024 ↔ 2025 comparison.")
        return

    # ── Side-by-side choropleth ───────────────────────────────────────────────
    st.markdown('<div class="sub-h">2024 actual ↔ 2025 projected</div>', unsafe_allow_html=True)

    val_max_24 = float(df24[col_c].quantile(0.95)) if df24[col_c].notna().any() else 1
    val_max_25 = float(df25[col_c].quantile(0.95)) if df25[col_c].notna().any() else 1
    val_max = max(val_max_24, val_max_25, 0.1)

    map_c1, map_c2 = st.columns(2)

    if gdf is not None:
        with map_c1:
            merged24 = gdf.merge(df24, on='sa3_code', how='left')
            fig24 = px.choropleth(
                merged24, geojson=merged24.__geo_interface__,
                locations=merged24.index, color=col_c,
                color_continuous_scale=cscale, range_color=[0, val_max],
                hover_data={'sa3_name': True, 'state': True, col_c: ':.2f'},
                title=f'{metric_label} — 2024 (actual)',
            )
            fig24.update_geos(fitbounds='locations', visible=False)
            theme(fig24, height=480)
            st.plotly_chart(fig24, use_container_width=True, key="ch5_map_24")

        with map_c2:
            merged25 = gdf.merge(df25[['sa3_code', 'sa3_name', 'state', col_c]], on='sa3_code', how='left')
            fig25 = px.choropleth(
                merged25, geojson=merged25.__geo_interface__,
                locations=merged25.index, color=col_c,
                color_continuous_scale=cscale, range_color=[0, val_max],
                hover_data={'sa3_name': True, 'state': True, col_c: ':.2f'},
                title=f'{metric_label} — 2025 (projected, {scenario})',
            )
            fig25.update_geos(fitbounds='locations', visible=False)
            theme(fig25, height=480)
            st.plotly_chart(fig25, use_container_width=True, key="ch5_map_25")
    else:
        st.info("Shapefile not loaded — choropleth unavailable.")

    # ── Movement KPIs ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="sub-h">2024 → 2025 movement</div>', unsafe_allow_html=True)

    cmp_ = (
        df24.rename(columns={col_c: '_24'})[['sa3_code', '_24']]
        .merge(df25[['sa3_code', col_c]].rename(columns={col_c: '_25'}), on='sa3_code', how='inner')
        .dropna()
    )

    if higher_is_better:
        n_imp = int((cmp_['_25'] > cmp_['_24']).sum())
        n_wor = int((cmp_['_25'] < cmp_['_24']).sum())
    else:
        n_imp = int((cmp_['_25'] < cmp_['_24']).sum())
        n_wor = int((cmp_['_25'] > cmp_['_24']).sum())
    n_tot = len(cmp_)
    n_tie = n_tot - n_imp - n_wor
    pct_wor = n_wor * 100 // n_tot if n_tot else 0
    pct_imp = n_imp * 100 // n_tot if n_tot else 0

    k1, k2, k3 = st.columns(3)
    k1.metric("SA3s Improved", str(n_imp), f"{pct_imp}% of {n_tot}",
              help=f"{metric_label} moved in the better direction 2024→2025 under {scenario}")
    k2.metric("SA3s Worsened", str(n_wor), f"{pct_wor}% of {n_tot}",
              delta_color="inverse",
              help=f"{metric_label} moved in the worse direction 2024→2025 under {scenario}")
    k3.metric("No Change / Tied", str(n_tie))

    if n_wor >= n_imp:
        st.warning(
            f"⚠️ Under **{scenario}**, **{n_wor} SA3s ({pct_wor}%)** will worsen "
            f"{metric_label} by 2025 if supply stays at 2024 levels."
        )
    else:
        st.success(
            f"✓ Under **{scenario}**, **{n_imp} SA3s ({pct_imp}%)** are projected to improve "
            f"{metric_label} by 2025."
        )

    # ── Top-10 movers ─────────────────────────────────────────────────────────
    st.markdown('<div class="sub-h">Top 10 SA3 regions moving most</div>', unsafe_allow_html=True)
    cmp_ = cmp_.merge(
        master[['sa3_code', 'sa3_name', 'state']].drop_duplicates('sa3_code'),
        on='sa3_code', how='left',
    )
    cmp_['delta'] = cmp_['_25'] - cmp_['_24']

    # For "worse" metrics (CGI), worse = higher; sort delta desc.
    # For "better" metrics, the worst is delta most negative.
    if higher_is_better:
        cmp_['movement_score'] = -cmp_['delta']
    else:
        cmp_['movement_score'] = cmp_['delta']

    top10 = (
        cmp_.dropna(subset=['sa3_name'])
        .nlargest(10, 'movement_score')
        [['sa3_name', 'state', '_24', '_25', 'delta']]
    )

    # Build styled HTML table matching dashboard theme
    rows_html = []
    for _r in top10.itertuples():
        d = float(_r.delta)
        # Direction: for "worse" metrics (CGI), positive delta = bad
        is_bad = (d > 0) if not higher_is_better else (d < 0)
        delta_col = C['red'] if is_bad else C['teal']
        sign = '+' if d > 0 else ('' if d == 0 else '−')
        delta_str = f'{sign}{abs(d):.2f}'
        rows_html.append(
            f'<tr style="border-bottom:1px solid {C["border"]}">'
            f'<td style="padding:10px 14px;color:{C["navy"]};font-weight:600">{_r.sa3_name}</td>'
            f'<td style="padding:10px 14px;color:{C["muted"]}">{_r.state}</td>'
            f'<td style="padding:10px 14px;text-align:right;color:{C["navy"]}">{_r._3:.2f}</td>'
            f'<td style="padding:10px 14px;text-align:right;color:{C["navy"]};font-weight:700">{_r._4:.2f}</td>'
            f'<td style="padding:10px 14px;text-align:right;color:{delta_col};font-weight:800">{delta_str}</td>'
            f'</tr>'
        )

    table_html = (
        f'<div style="border:1px solid {C["border"]};border-radius:12px;overflow:hidden;'
        f'background:{C["white"]};box-shadow:0 1px 4px rgba(0,0,0,0.04);margin-top:8px">'
        f'<table style="width:100%;border-collapse:collapse;font-size:14px;'
        f'font-family:Inter,-apple-system,sans-serif">'
        f'<thead><tr style="background:{C["navy"]}">'
        f'<th style="padding:12px 14px;text-align:left;color:white;font-weight:700">SA3</th>'
        f'<th style="padding:12px 14px;text-align:left;color:white;font-weight:700">State</th>'
        f'<th style="padding:12px 14px;text-align:right;color:white;font-weight:700">2024</th>'
        f'<th style="padding:12px 14px;text-align:right;color:white;font-weight:700">2025</th>'
        f'<th style="padding:12px 14px;text-align:right;color:white;font-weight:700">Δ</th>'
        f'</tr></thead><tbody>'
        + ''.join(rows_html) +
        f'</tbody></table></div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)
