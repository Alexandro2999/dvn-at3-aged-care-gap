"""Standalone interactive SA3 choropleth — embedded in Home and Ch1.

Renders a full-screen Australia map with:
    - Metric toggle (Care Gap Index, Access Rate, Quality Score, Beds/1k,
      Waitlist Pressure) via a radio that separates projected vs real metrics
    - Year toggle 2023→2025; the 📈 marker indicates 2025 forecast values
    - SA3 hover card with state, MMM band, and the active metric
    - Session-state-driven re-render guard so the map renders on first load
      (Streamlit map widgets normally need a first interaction to paint)

2025 values are computed via `build_master_2025` against the selected
scenario growth rate; pre-2025 years are always real data.
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from tabs.utils import C, theme, build_master_2025, SCENARIO_GROWTH_RATES

# Major Australian cities — visual orientation markers on the choropleth.
_CITIES = [
    ('Sydney',    -33.87, 151.21),
    ('Melbourne', -37.81, 144.96),
    ('Brisbane',  -27.47, 153.03),
    ('Perth',     -31.95, 115.86),
    ('Adelaide',  -34.93, 138.60),
    ('Canberra',  -35.28, 149.13),
    ('Hobart',    -42.88, 147.33),
    ('Darwin',    -12.46, 130.84),
]

# (label, col_name, cscale, colorbar_label, src, higher_is_better, projected_at_2025)
# projected_at_2025 = True when 2025 isn't real data → relies on Ch5 build_master_2025.
_METRIC_DEFS = [
    ('Care Gap Index',         'care_gap_index',       [[0,'#EAF0F5'],[0.4,'#3D6FA0'],[1,'#11304E']], 'Care Gap Index',      'df',           False, True),
    ('Quality Score',          'quality_score',        [[0,'#FBF6E5'],[0.5,'#D9A53B'],[1,'#7A5A12']], 'Quality Score',       'df',           True,  False),
    ('Residential Access Rate','access_rate',          [[0,'#E7F3F1'],[0.5,'#2BA39B'],[1,'#0E5A55']], 'Residential Access %','df',           True,  True),
    ('Waitlist Pressure',      'waitlist_pressure',    [[0,'#FBEEEC'],[0.5,'#C44A38'],[1,'#7A2D24']], 'Waitlist Pressure',   'waitlist',      False, False),
    ('Beds per 1,000 elderly', 'beds_per_1k',          [[0,'#EAF0F5'],[0.5,'#3D6FA0'],[1,'#11304E']], 'Beds / 1k elderly',  'supply',        True,  True),
    ('Number of Facilities',   'n_facilities',         [[0,'#E7F3F1'],[0.5,'#2BA39B'],[1,'#0E5A55']], 'Facilities',         'supply_nopop',  True,  False),
]

# Per-metric explainer: (formula, plain-English interpretation)
_METRIC_INFO = {
    'Care Gap Index': (
        'residential_access_rate ÷ quality_score',
        'Composite indicator of unmet need. <b>Higher value = region is underserved</b> '
        '(high demand relative to low quality). Values &gt; 1 flag concern.',
    ),
    'Quality Score': (
        'mean of 4 ACQSC sub-ratings (Residents\' Experience, Staffing, Compliance, Quality Measures)',
        'Average facility rating in the region, on a 0–5 ★ scale. <b>Higher = better quality of care.</b>',
    ),
    'Residential Access Rate': (
        '(total_residential ÷ pop_65_plus) × 100',
        'Share of the 65+ population currently living in residential aged care. '
        '<b>Higher = more elderly placed in residential beds locally.</b>',
    ),
    'Waitlist Pressure': (
        'hcp_high_needs ÷ residential_places',
        'High-needs home-care users per residential bed. '
        '<b>Values &gt; 1.0 = crisis zone</b> — demand outpaces local supply.',
    ),
    'Beds per 1,000 elderly': (
        '(residential_places ÷ pop_65_plus) × 1,000',
        'Residential supply density. <b>Higher = more beds available per 1,000 people aged 65+.</b>',
    ),
    'Number of Facilities': (
        'count of aged-care services in the SA3 (residential + home-care combined)',
        'Service points operating in the region. <b>Higher = more provider presence.</b>',
    ),
}


def _project_df_to_2025(df, supply, service_users, ratings, population, scenario):
    """Return df with a projected 2025 row appended via the given Ch5 scenario.
    Silent fallback to original df if projection fails."""
    if ratings is None or service_users is None or 2025 in df['year'].unique():
        return df
    try:
        df_2025 = build_master_2025(
            df, supply, service_users, ratings, population, scenario=scenario,
        )
        df_2025 = df_2025.copy()
        df_2025['year'] = 2025
        keep_cols = [c for c in df.columns if c in df_2025.columns]
        return pd.concat([df, df_2025[keep_cols]], ignore_index=True)
    except Exception:
        return df


def _build_waitlist_frame(service_users, supply):
    """Waitlist pressure = hcp_high_needs / residential_places, no pop_65 dependency.
    Covers every year present in BOTH service_users and supply (typically 2023–2025)."""
    if service_users is None or service_users.empty:
        return pd.DataFrame(columns=['sa3_code', 'year', 'waitlist_pressure'])
    su = service_users[['sa3_code', 'year', 'hcp_high_needs']].copy()
    sp = supply[['sa3_code', 'year', 'residential_places']].copy()
    wp = su.merge(sp, on=['sa3_code', 'year'], how='inner')
    wp = wp[wp['residential_places'] > 0].copy()
    wp['waitlist_pressure'] = wp['hcp_high_needs'] / wp['residential_places']
    return wp[['sa3_code', 'year', 'waitlist_pressure']]


def _build_map_data(metric_key, col_c, src_c, year_c, df, supply, population, sa3_meta,
                    wp_frame=None):
    if src_c == 'df':
        df_c = df[df['year'] == year_c].copy()
        keep = [c for c in ['sa3_code', col_c, 'sa3_name', 'state', 'mmm_code', 'pop_65_plus'] if c in df_c.columns]
        return df_c[keep]
    elif src_c == 'waitlist':
        wp_yr = (wp_frame if wp_frame is not None else pd.DataFrame())
        wp_yr = wp_yr[wp_yr['year'] == year_c][['sa3_code', 'waitlist_pressure']]
        # inner join — only keep SA3 codes in the (filtered) sa3_meta
        return wp_yr.merge(sa3_meta, on='sa3_code', how='inner')
    elif src_c == 'supply':
        # Prefer df (master) when year is in it — handles 2025 projected via build_master_2025
        if 'beds_per_1k' in df.columns and year_c in df['year'].unique():
            df_c = df[df['year'] == year_c][['sa3_code', 'beds_per_1k']].copy()
            return df_c.merge(sa3_meta, on='sa3_code', how='inner')
        _s = supply.merge(population[['sa3_code', 'year', 'pop_65_plus']], on=['sa3_code', 'year'], how='inner')
        _s = _s[_s['pop_65_plus'] > 0].copy()
        _s['beds_per_1k'] = _s['residential_places'] / _s['pop_65_plus'] * 1000
        _s_yr = _s[_s['year'] == year_c][['sa3_code', 'beds_per_1k']]
        return _s_yr.merge(sa3_meta, on='sa3_code', how='inner')
    else:  # supply_nopop
        _s_yr = supply[supply['year'] == year_c][['sa3_code', 'n_facilities']]
        # inner join — drop SA3s not in filtered sa3_meta
        return _s_yr.merge(sa3_meta, on='sa3_code', how='inner')


def _movement_kpis(col_c, src_c, higher_is_better, metric_label, year_c, year_prev,
                   df, supply, population, sa3_meta, wp_frame=None):
    """Render 3 movement KPI cards + callout for the selected metric and year pair."""
    st.markdown(
        f'<div class="sub-h">{year_prev} → {year_c} {metric_label} Movement</div>',
        unsafe_allow_html=True,
    )

    # Build two-year data frames
    if src_c == 'df':
        _curr = df[df['year'] == year_c][['sa3_code', col_c]].rename(columns={col_c: '_curr'})
        _prev = df[df['year'] == year_prev][['sa3_code', col_c]].rename(columns={col_c: '_prev'})
        _delta = _prev.merge(_curr, on='sa3_code', how='inner').dropna(subset=['_prev', '_curr'])
    elif src_c == 'waitlist':
        wp = wp_frame if wp_frame is not None else pd.DataFrame(columns=['sa3_code', 'year', 'waitlist_pressure'])
        _curr = wp[wp['year'] == year_c][['sa3_code', 'waitlist_pressure']].rename(columns={'waitlist_pressure': '_curr'})
        _prev = wp[wp['year'] == year_prev][['sa3_code', 'waitlist_pressure']].rename(columns={'waitlist_pressure': '_prev'})
        _delta = _prev.merge(_curr, on='sa3_code', how='inner').dropna(subset=['_prev', '_curr'])
    elif src_c == 'supply':
        if 'beds_per_1k' in df.columns and year_c in df['year'].unique() and year_prev in df['year'].unique():
            _curr = df[df['year'] == year_c][['sa3_code', 'beds_per_1k']].rename(columns={'beds_per_1k': '_curr'})
            _prev = df[df['year'] == year_prev][['sa3_code', 'beds_per_1k']].rename(columns={'beds_per_1k': '_prev'})
        else:
            _s = supply.merge(population[['sa3_code', 'year', 'pop_65_plus']], on=['sa3_code', 'year'], how='inner')
            _s = _s[_s['pop_65_plus'] > 0].copy()
            _s['beds_per_1k'] = _s['residential_places'] / _s['pop_65_plus'] * 1000
            _curr = _s[_s['year'] == year_c][['sa3_code', 'beds_per_1k']].rename(columns={'beds_per_1k': '_curr'})
            _prev = _s[_s['year'] == year_prev][['sa3_code', 'beds_per_1k']].rename(columns={'beds_per_1k': '_prev'})
        _delta = _prev.merge(_curr, on='sa3_code', how='inner').dropna(subset=['_prev', '_curr'])
    else:  # supply_nopop
        _curr = supply[supply['year'] == year_c][['sa3_code', 'n_facilities']].rename(columns={'n_facilities': '_curr'})
        _prev = supply[supply['year'] == year_prev][['sa3_code', 'n_facilities']].rename(columns={'n_facilities': '_prev'})
        _delta = _prev.merge(_curr, on='sa3_code', how='inner').dropna(subset=['_prev', '_curr'])

    if _delta.empty:
        st.info(f"Movement data not available for {year_prev}→{year_c}.")
        return

    if higher_is_better:
        n_imp = int((_delta['_curr'] > _delta['_prev']).sum())
        n_wor = int((_delta['_curr'] < _delta['_prev']).sum())
    else:
        n_imp = int((_delta['_curr'] < _delta['_prev']).sum())
        n_wor = int((_delta['_curr'] > _delta['_prev']).sum())

    n_total = len(_delta)
    n_tie   = n_total - n_imp - n_wor
    pct_imp = n_imp * 100 // n_total if n_total else 0
    pct_wor = n_wor * 100 // n_total if n_total else 0

    kc1, kc2, kc3 = st.columns(3)
    kc1.metric(
        "SA3s Improved",
        str(n_imp),
        f"{pct_imp}% of {n_total} regions",
        help=f"{metric_label} moved in the better direction {year_prev}→{year_c}",
    )
    kc2.metric(
        "SA3s Worsened",
        str(n_wor),
        f"{pct_wor}% of {n_total} regions",
        delta_color="inverse",
        help=f"{metric_label} moved in the worse direction {year_prev}→{year_c}",
    )
    kc3.metric(
        "No Change / Tied",
        str(n_tie),
        help=f"SA3s with identical {metric_label} both years",
    )



def render(df, gdf, supply, population, service_users=None, ratings=None, show_movement=True) -> None:
    st.markdown('<div class="sec-h1">Interactive Map</div>', unsafe_allow_html=True)

    # ── Data type radio: which metrics show, based on 2025 source ──────────
    scenario_options = list(SCENARIO_GROWTH_RATES.keys())
    _PROJ_LABEL = "📈 2025 forecast"
    _REAL_LABEL = "Real 2025 data"

    def _on_data_type_change():
        # When user toggles data type, snap fm_metric to a valid option in the new pool.
        new_type = st.session_state.get('fm_data_type', _PROJ_LABEL)
        if new_type.startswith("📈"):
            new_pool = [m for m in _METRIC_DEFS if m[6]]
        else:
            new_pool = [m for m in _METRIC_DEFS if not m[6]]
        if new_pool and st.session_state.get('fm_metric') not in [m[0] for m in new_pool]:
            st.session_state['fm_metric'] = new_pool[0][0]

    # All controls grouped inside a bordered card
    controls_card = st.container(border=True)
    with controls_card:
        data_type = st.radio(
            "Data type",
            options=[_PROJ_LABEL, _REAL_LABEL],
            horizontal=True,
            key="fm_data_type",
            on_change=_on_data_type_change,
            help="📈 Forecast = metrics where 2025 is computed from ABS trends "
                 "(Care Gap, Access, Beds per 1k — they need pop_65_plus which ABS hasn't released). "
                 "Real 2025 = metrics where actual 2025 data exists (Quality, Waitlist, Facilities).",
        )
        with st.expander("📈 What's real vs projected in 2025?"):
            st.markdown(
                "**✅ Real 2025 data** (used as-is)\n"
                "- **Quality Score** — from the Feb 2026 star ratings snapshot\n"
                "- **Waitlist Pressure** — from AIHW home-care user counts\n"
                "- **Facilities** — from AIHW service list\n"
                "\n"
                "**🔮 Projected** (estimated, because ABS hasn't released 2025 population yet)\n"
                "- **Population aged 65+** — 2024 figures grown forward using each state's "
                "2023→2024 trend\n"
                "- **Access Rate · Care Gap · Beds per 1,000** — recomputed using the projected "
                "65+ population\n"
                "\n"
                "Use the **sidebar scenario picker** to test how fast the 65+ group grows: "
                "*Baseline* (ABS trend), *Aggressive aging* (+4%/yr), or *Stagnation* (0%)."
            )
    is_projected_mode = data_type.startswith("📈")
    metric_pool = [m for m in _METRIC_DEFS if (m[6] if is_projected_mode else not m[6])]

    # Read scenario from session state for projection (picker renders below if needed)
    scenario = st.session_state.get('fm_scenario', scenario_options[0])
    if scenario not in scenario_options:
        scenario = scenario_options[0]

    # ── Project df to include a 2025 row using selected scenario ───────────
    with st.spinner("Recomputing 2025 forecast..."):
        df = _project_df_to_2025(df, supply, service_users, ratings, population, scenario)

    # ── Build waitlist frame (uses service_users + supply, no pop dependency) ─
    wp_frame = _build_waitlist_frame(service_users, supply)
    # Respect global filter — keep only SA3 codes present in (filtered) df
    _allowed_sa3 = set(df['sa3_code'].dropna().unique())
    if not wp_frame.empty:
        wp_frame = wp_frame[wp_frame['sa3_code'].isin(_allowed_sa3)]
    # Same filter on supply (used directly by 'supply_nopop' metric + Movement KPIs)
    supply = supply[supply['sa3_code'].isin(_allowed_sa3)].copy()

    # ── Derive available years dynamically ────────────────────────────────────
    _df_years   = sorted(df['year'].dropna().unique().tolist())
    _sup_years  = sorted(supply['year'].dropna().unique().tolist())
    _pop_years  = sorted(population['year'].dropna().unique().tolist())
    _beds_years = sorted(set(_sup_years) & set(_pop_years))
    if 2025 in _df_years and 2025 not in _beds_years:
        _beds_years = sorted(_beds_years + [2025])
    _wp_years   = sorted(int(y) for y in wp_frame['year'].dropna().unique()) if not wp_frame.empty else _df_years

    _YEAR_MAP = {'df': _df_years, 'waitlist': _wp_years,
                 'supply': _beds_years, 'supply_nopop': _sup_years}

    # ── Metric / Year / (Scenario) row + Definition (all inside controls card) ─
    metric_options = {
        label: (col, cscale, cbar, src, higher_is_better, label, is_proj)
        for label, col, cscale, cbar, src, higher_is_better, is_proj in metric_pool
    }
    with controls_card:
        if is_projected_mode:
            sel_metric, sel_year, sel_scenario = st.columns([2, 1, 2])
        else:
            sel_metric, sel_year = st.columns([2, 1])
            sel_scenario = None

        with sel_metric:
            metric_sel = st.selectbox(
                "Colour map by", options=list(metric_options.keys()), index=0, key="fm_metric",
            )
        col_c, cscale_c, cbar_c, src_c, higher_is_better, metric_label, is_proj_metric = metric_options[metric_sel]
        avail_years = _YEAR_MAP[src_c]

        # Force one extra rerun on metric change so the year dropdown and
        # "No data" check both see the fresh metric state. Streamlit's selectbox
        # cached value lags by one render otherwise.
        _prev_metric = st.session_state.get('_fm_last_metric')
        st.session_state['_fm_last_metric'] = metric_sel
        if _prev_metric is not None and _prev_metric != metric_sel:
            _y_state = st.session_state.get('fm_year')
            if _y_state is None or _y_state not in avail_years:
                st.session_state['fm_year'] = int(avail_years[-1])
            st.rerun()

        with sel_year:
            year_c = st.selectbox(
                "Year",
                options=[int(y) for y in avail_years],
                index=len(avail_years) - 1,
                key="fm_year",
                format_func=lambda y: f'{y} 📈' if (is_proj_metric and y == 2025) else str(y),
            )

        if is_projected_mode and sel_scenario is not None:
            with sel_scenario:
                scenario = st.selectbox(
                    "Projection scenario",
                    options=scenario_options,
                    index=scenario_options.index(scenario),
                    key="fm_scenario",
                    help="Per-state CAGR applied to pop_65_plus when projecting 2025.",
                )

        # Per-metric definition (updates with each metric selection)
        if metric_sel in _METRIC_INFO:
            _formula, _interp = _METRIC_INFO[metric_sel]
            st.markdown(
                f'<div style="background:#F0F8F5;'
                f'border-left:5px solid #2BA39B;border-radius:8px;'
                f'padding:14px 18px;margin:20px 18px 12px;'
                f'box-shadow:0 1px 3px rgba(0,0,0,0.06);'
                f'color:{C["navy"]};font-size:20px;line-height:1.65">'
                f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:4px">'
                f'<span style="font-weight:800;font-size:21px;color:#11304E">📊 {metric_sel}</span>'
                f'<span style="font-family:Consolas,Menlo,monospace;background:#11304E;'
                f'color:#FFFFFF;padding:3px 10px;border-radius:14px;font-size:17.5px;'
                f'font-weight:600;letter-spacing:0.2px">{_formula}</span>'
                f'</div>'
                f'<span style="color:#4A5A6E">{_interp}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Forecast note shown above the map (only when projected + 2025) ────────
    if is_proj_metric and year_c == 2025:
        st.markdown(
            f'<div style="background:#FBF6E5;border-left:4px solid #D9A53B;'
            f'padding:14px 18px;border-radius:8px;margin:18px 0 16px;'
            f'color:{C["navy"]};font-size:19.5px;line-height:1.55">'
            f'📈 <b>You are viewing a 2025 forecast.</b> '
            f'<b>{metric_label}</b> for 2025 is computed using the <b>{scenario}</b> scenario '
            f'applied to ABS pop_65_plus growth. '
            f'Switch to <i>Real 2025 data</i> above to view metrics with actual 2025 values.'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Build map data ────────────────────────────────────────────────────────
    sa3_meta = df[['sa3_code', 'sa3_name', 'state', 'mmm_code']].drop_duplicates('sa3_code')
    map_data = _build_map_data(metric_sel, col_c, src_c, year_c, df, supply, population, sa3_meta,
                                wp_frame=wp_frame)

    # ── Movement KPIs above the map (dynamic, tied to selected metric + year) ─
    if show_movement:
        year_prev = year_c - 1
        if year_prev in avail_years:
            _movement_kpis(
                col_c, src_c, higher_is_better, metric_label,
                year_c, year_prev, df, supply, population, sa3_meta,
                wp_frame=wp_frame,
            )
        else:
            if avail_years:
                _avail_str = ", ".join(str(y) for y in avail_years)
                st.info(
                    f"📊 Year-on-year movement requires two consecutive years of data. "
                    f"For **{metric_label}**, data is only available for: {_avail_str}. "
                    f"Pick a year after {avail_years[0]} to see how SA3s shifted."
                )
            else:
                st.info(f"No {metric_label} data available under the current filter.")
        st.markdown("")  # small gap

    # ── Choropleth ────────────────────────────────────────────────────────────
    if gdf is not None and not map_data.empty and col_c in map_data.columns:
        val_max = float(map_data[col_c].quantile(0.95)) if map_data[col_c].notna().any() else 5
        hover = {k: True for k in ['sa3_name', 'state', 'mmm_code'] if k in map_data.columns}

        proj_marker = ' 📈' if is_proj_metric and year_c == 2025 else ''
        geojson_data = gdf.__geo_interface__
        fig_map = px.choropleth_mapbox(
            map_data,
            geojson=geojson_data,
            locations='sa3_code',
            featureidkey='properties.sa3_code',
            color=col_c,
            color_continuous_scale=cscale_c,
            range_color=[0, max(val_max, 0.1)],
            hover_data=hover,
            title=f'{metric_label} by SA3 — {year_c}{proj_marker}',
            labels={col_c: cbar_c},
            mapbox_style='carto-positron',
            center={'lat': -27, 'lon': 134},
            zoom=3,
            opacity=0.75,
        )
        fig_map.update_coloraxes(colorbar_title_text=cbar_c)

        # Overlay major cities for visual orientation
        fig_map.add_trace(go.Scattermapbox(
            lon=[c[2] for c in _CITIES],
            lat=[c[1] for c in _CITIES],
            text=[c[0] for c in _CITIES],
            mode='markers+text',
            marker=dict(size=8, color=C['navy']),
            textposition='top right',
            textfont=dict(size=14, color=C['navy']),
            hoverinfo='text',
            showlegend=False,
            name='Major cities',
        ))

        theme(fig_map, height=580)
        st.plotly_chart(fig_map, use_container_width=True, key="fm_map")
    elif not map_data.empty:
        st.info("GeoJSON not loaded — map unavailable.")
    else:
        st.warning(
            "**No SA3s match your sidebar filter for this year/metric.** "
            "Try expanding State or Remoteness in the left panel, or switch year/metric above."
        )

