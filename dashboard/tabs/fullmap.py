import pandas as pd
import streamlit as st
import plotly.express as px
from tabs.utils import C, theme

# (col_name, colorscale, colorbar_label, src, avail_years_fn, higher_is_better)
# avail_years_fn is a string key resolved at render time from dynamic year lists
_METRIC_DEFS = [
    ('Care Gap Index',         'care_gap_index',       [[0,'#E3F1FA'],[0.4,'#4A7FC1'],[1,'#1B3F6E']], 'Care Gap Index',      'df',           False),
    ('Quality Score',          'quality_score',        [[0,'#FFF5E6'],[0.5,'#F5A623'],[1,'#8B4500']], 'Quality Score ★',     'df',           True),
    ('Residential Access Rate','access_rate',          [[0,'#F0FFF0'],[0.5,'#4CAF50'],[1,'#1B5E20']], 'Residential Access %','df',           True),
    ('Waitlist Pressure',      'waitlist_pressure',    [[0,'#FFF0F0'],[0.5,'#E57373'],[1,'#7F0000']], 'Waitlist Pressure',   'waitlist',      False),
    ('Beds per 1,000 elderly', 'beds_per_1k',          [[0,'#E3F1FA'],[0.5,'#4A7FC1'],[1,'#1B3F6E']], 'Beds / 1k elderly',  'supply',        True),
    ('Number of Facilities',   'n_facilities',         [[0,'#E6F4F1'],[0.5,'#00A79D'],[1,'#005F5A']], 'Facilities',         'supply_nopop',  True),
]


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
        return wp_yr.merge(sa3_meta, on='sa3_code', how='left')
    elif src_c == 'supply':
        _s = supply.merge(population[['sa3_code', 'year', 'pop_65_plus']], on=['sa3_code', 'year'], how='inner')
        _s = _s[_s['pop_65_plus'] > 0].copy()
        _s['beds_per_1k'] = _s['residential_places'] / _s['pop_65_plus'] * 1000
        _s_yr = _s[_s['year'] == year_c][['sa3_code', 'beds_per_1k']]
        return _s_yr.merge(sa3_meta, on='sa3_code', how='left')
    else:  # supply_nopop
        _s_yr = supply[supply['year'] == year_c][['sa3_code', 'n_facilities']]
        return _s_yr.merge(sa3_meta, on='sa3_code', how='left')


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

    if n_imp >= n_wor:
        st.success(
            f"**{n_imp} SA3s ({pct_imp}%) improved** {metric_label} from {year_prev}→{year_c}. "
            f"The **{n_wor} worsening SA3s** may signal areas of continued structural pressure."
        )
    else:
        st.warning(
            f"**{n_wor} SA3s ({pct_wor}%) worsened** {metric_label} from {year_prev}→{year_c}. "
            f"Only {n_imp} SA3s ({pct_imp}%) showed improvement over this period."
        )


def render(df, gdf, supply, population, service_users=None) -> None:
    st.markdown('<div class="sec-h1">Interactive Map</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sec-p">Explore aged care outcomes across every SA3 region in Australia. '
        'Switch metrics and years to reveal where supply is collapsing, '
        'where quality is falling, and where demand outstrips capacity.</p>',
        unsafe_allow_html=True,
    )

    # ── Build waitlist frame (uses service_users + supply, no pop dependency) ─
    wp_frame = _build_waitlist_frame(service_users, supply)

    # ── Derive available years dynamically ────────────────────────────────────
    _df_years   = sorted(df['year'].dropna().unique().tolist())
    _sup_years  = sorted(supply['year'].dropna().unique().tolist())
    _pop_years  = sorted(population['year'].dropna().unique().tolist())
    _beds_years = sorted(set(_sup_years) & set(_pop_years))
    _wp_years   = sorted(int(y) for y in wp_frame['year'].dropna().unique()) if not wp_frame.empty else _df_years
    _df_rng     = f"{_df_years[0]}–{_df_years[-1]}"
    _beds_rng   = f"{_beds_years[0]}–{_beds_years[-1]}"
    _fac_rng    = f"{_sup_years[0]}–{_sup_years[-1]}"
    _wp_rng     = f"{_wp_years[0]}–{_wp_years[-1]}" if _wp_years else _df_rng

    _YEAR_MAP = {'df': _df_years, 'waitlist': _wp_years,
                 'supply': _beds_years, 'supply_nopop': _sup_years}
    _RANGE_LABEL = {'df': _df_rng, 'waitlist': _wp_rng,
                    'supply': _beds_rng, 'supply_nopop': _fac_rng}

    # ── Metric selectbox ──────────────────────────────────────────────────────
    metric_options = {
        f'{label}  ({_RANGE_LABEL[src]})': (col, cscale, cbar, src, higher_is_better, label)
        for label, col, cscale, cbar, src, higher_is_better in _METRIC_DEFS
    }

    sel_c1, sel_c2 = st.columns([3, 1])
    with sel_c1:
        metric_sel = st.selectbox(
            "Colour map by", options=list(metric_options.keys()), index=0, key="fm_metric",
        )
    col_c, cscale_c, cbar_c, src_c, higher_is_better, metric_label = metric_options[metric_sel]
    avail_years = _YEAR_MAP[src_c]

    with sel_c2:
        year_c = st.selectbox(
            "Year",
            options=[int(y) for y in avail_years],
            index=len(avail_years) - 1,
            key="fm_year",
        )

    # ── Build map data ────────────────────────────────────────────────────────
    sa3_meta = df[['sa3_code', 'sa3_name', 'state', 'mmm_code']].drop_duplicates('sa3_code')
    map_data = _build_map_data(metric_sel, col_c, src_c, year_c, df, supply, population, sa3_meta,
                                wp_frame=wp_frame)

    # ── Choropleth ────────────────────────────────────────────────────────────
    if gdf is not None and not map_data.empty and col_c in map_data.columns:
        merged = gdf.merge(map_data, on='sa3_code', how='left')
        val_max = float(map_data[col_c].quantile(0.95)) if map_data[col_c].notna().any() else 5
        hover = {k: True for k in ['sa3_name', 'state', 'mmm_code'] if k in merged.columns}
        for extra in ['care_gap_index', 'quality_score', 'access_rate']:
            if extra != col_c and extra in merged.columns:
                hover[extra] = ':.2f'

        fig_map = px.choropleth(
            merged,
            geojson=merged.__geo_interface__,
            locations=merged.index,
            color=col_c,
            color_continuous_scale=cscale_c,
            range_color=[0, max(val_max, 0.1)],
            hover_data=hover,
            title=f'{metric_label} by SA3 — {year_c}',
            labels={col_c: cbar_c},
        )
        fig_map.update_geos(fitbounds='locations', visible=False)
        fig_map.update_coloraxes(colorbar_title_text=cbar_c)
        theme(fig_map, height=580)
        st.plotly_chart(fig_map, use_container_width=True, key="fm_map")
    elif not map_data.empty:
        st.info("Shapefile not loaded — map unavailable. Run `load_shapefile()` from inside `dashboard/`.")
    else:
        st.info("No data available for the current filter and year selection.")

    # ── Movement KPIs (dynamic, tied to selected metric + year) ───────────────
    st.markdown("---")
    year_prev = year_c - 1
    prev_available = year_prev in avail_years

    if prev_available:
        _movement_kpis(
            col_c, src_c, higher_is_better, metric_label,
            year_c, year_prev, df, supply, population, sa3_meta,
            wp_frame=wp_frame,
        )
    else:
        st.info(
            f"Movement data not available — no {metric_label} data for {year_prev}. "
            f"Select a later year to see year-on-year changes."
        )
