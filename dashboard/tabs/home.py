import streamlit as st
import plotly.graph_objects as go

from tabs.utils import C, SCENARIO_GROWTH_RATES
import tabs.fullmap as pg_fullmap
from tabs.fullmap import _project_df_to_2025


MMM_LABELS = {
    'MM1': 'Major City', 'MM2': 'Inner Regional', 'MM3': 'Outer Regional',
    'MM4': 'Remote', 'MM5': 'Small Rural', 'MM6': 'Remote Community', 'MM7': 'Very Remote',
}


_ORG_COLOUR = {'profit': '#E67E22', 'not_for_profit': '#11304E', 'government': '#2BA39B'}
_ORG_LABEL  = {'profit': 'For Profit', 'not_for_profit': 'Not for Profit', 'government': 'Government'}


def _mini_trend(years, values, title, line_colour='#11304E', value_fmt=':.2f'):
    """Small clean line+marker trend chart with integer year labels and auto y-range."""
    fmt = '{:' + value_fmt.lstrip(':') + '}'
    text_labels = [fmt.format(v) if v == v else '' for v in values]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=values, mode='lines+markers+text',
        line=dict(color=line_colour, width=2.5),
        marker=dict(size=8, color=line_colour),
        text=text_labels, textposition='top center',
        textfont=dict(size=14, color=line_colour),
        hovertemplate='%{x}: %{y}<extra></extra>',
        showlegend=False,
    ))
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=16, color='#11304E', family='Inter')),
        height=160,
        margin=dict(l=10, r=10, t=32, b=24),
        plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
        xaxis=dict(
            tickmode='array', tickvals=list(years),
            ticktext=[str(int(y)) for y in years],
            showgrid=False, zeroline=False,
            tickfont=dict(size=14, color='#6B7C93'),
        ),
        yaxis=dict(
            showgrid=True, gridcolor='#EDEFF3', zeroline=False,
            tickfont=dict(size=14, color='#6B7C93'),
            automargin=True,
        ),
    )
    return fig


def _band_for_percentile(pct):
    """Return (label, colour) for a percentile rank (0=best, 1=worst)."""
    if pct <= 0.25:
        return "Top 25% (better than most)", "#2BA39B"
    if pct <= 0.75:
        return "Middle 50%", "#D9A53B"
    return "Bottom 25% (worse than most)", "#C44A38"


def _render_find_my_area(df, ratings, supply=None, population=None, service_users=None):
    """SA3 search → KPI cards with comparison context, crisis warning,
    trend mini-charts, and filterable top facilities table."""
    if df is None or df.empty:
        st.info("No SA3 data available for Find My Area.")
        return

    # Project df to include 2025 row (idempotent if 2025 already present)
    if supply is not None and population is not None and service_users is not None:
        scenario = st.session_state.get('fm_scenario', list(SCENARIO_GROWTH_RATES.keys())[0])
        with st.spinner("Recomputing 2025 forecast..."):
            df = _project_df_to_2025(df, supply, service_users, ratings, population, scenario)

    # ── Year mode toggle (Real vs Forecast) ─────────────────────────────────
    available_years = sorted(int(y) for y in df['year'].dropna().unique())
    real_year = max((y for y in available_years if y != 2025), default=available_years[0])
    has_forecast = 2025 in available_years

    if has_forecast:
        c_year, c_search = st.columns([1.2, 2.8])
        with c_year:
            year_mode = st.radio(
                "Data type",
                options=[f"Real {real_year}", "📈 Forecast 2025"],
                horizontal=True,
                key="fma_year_mode",
                help=f"Real {real_year} = actual data. 📈 Forecast 2025 = "
                     f"Care Gap & Access projected from ABS trend (Quality is real).",
            )
            with st.expander("📈 What's real vs projected in 2025?"):
                st.markdown(
                    "**✅ Real** — Quality Score (from Feb 2026 ratings).\n"
                    "\n"
                    "**🔮 Projected** — 65+ population, Access Rate, Care Gap, Beds per 1,000.\n"
                    "We grow 2024 ABS population forward using each state's 2019–2024 trend, "
                    "then recompute the rate metrics.\n"
                    "\n"
                    "Change the **sidebar scenario** to test growth: *Baseline* (ABS trend), "
                    "*Aggressive aging* (+4%/yr), or *Stagnation* (0%)."
                )
        is_forecast = year_mode.startswith("📈")
    else:
        c_search = st.container()
        is_forecast = False

    year_used = 2025 if is_forecast else real_year
    proj_marker = " 📈" if is_forecast else ""

    df_yr = df[df['year'] == year_used].drop_duplicates('sa3_name').copy()
    _sa3_opts = [""] + sorted(df_yr['sa3_name'].dropna().unique().tolist())

    with c_search:
        search = st.selectbox(
            "Find your area",
            options=_sa3_opts,
            index=0,
            key="home_sa3_search",
            format_func=lambda x: "— type to search SA3 name —" if x == "" else x,
            help=(
                "SA3 = Statistical Area Level 3 (~330 regions Australia-wide). "
                "Search by SA3 name, e.g. 'Sydney - Eastern Suburbs', "
                "'Noosa Hinterland'. Not the same as a city or postcode."
            ),
        )
    if not search:
        return

    row = df_yr[df_yr['sa3_name'] == search].iloc[0]
    state = row.get('state', '')

    # ── Crisis-zone warning (waitlist_pressure > 1.0) ───────────────────────
    wp = row.get('waitlist_pressure')
    hcp = row.get('hcp_high_needs')
    beds = row.get('residential_places')
    if wp is not None and wp == wp and wp > 1.0:  # not NaN and > 1
        st.markdown(
            f'<div style="background:#FDECEA;border-left:5px solid #C44A38;'
            f'border-radius:8px;padding:12px 16px;margin:10px 0 16px;'
            f'color:{C["navy"]};font-size:20px;line-height:1.55">'
            f'⚠️ <b>Crisis zone</b> — this region has more high-needs home-care users '
            f'than residential beds. '
            f'<b>{int(hcp) if hcp == hcp else "—"}</b> high-needs HCP users vs '
            f'<b>{int(beds) if beds == beds else "—"}</b> residential places '
            f'(waitlist pressure ratio <b>{wp:.2f}</b>).'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Compute comparison context (rank + averages) ────────────────────────
    valid = df_yr.dropna(subset=['care_gap_index']).copy()
    valid['_rank'] = valid['care_gap_index'].rank(ascending=False, method='min')
    total_sa3 = len(valid)
    rank = int(valid[valid['sa3_name'] == search]['_rank'].iloc[0]) if not valid[valid['sa3_name'] == search].empty else None
    pct = (rank / total_sa3) if rank else None
    band_label, band_colour = (_band_for_percentile(pct) if pct is not None else ("—", "#6B7C93"))

    nat_gap   = df_yr['care_gap_index'].mean()
    nat_qual  = df_yr['quality_score'].mean()
    nat_acc   = df_yr['access_rate'].mean()
    state_gap = df_yr[df_yr['state'] == state]['care_gap_index'].mean()
    state_qual = df_yr[df_yr['state'] == state]['quality_score'].mean()
    state_acc = df_yr[df_yr['state'] == state]['access_rate'].mean()

    st.markdown(
        f'<div style="margin:8px 0 6px;color:{C["navy"]};font-size:21px">'
        f'<b style="font-size:23px">{search}</b> '
        f'<span style="color:#6B7C93">({state} · {MMM_LABELS.get(row.get("mmm_code", ""), row.get("mmm_code", ""))})</span>'
        f'&nbsp;&nbsp;'
        f'<span style="background:{band_colour};color:#FFFFFF;padding:3px 10px;'
        f'border-radius:12px;font-size:17.5px;font-weight:700">'
        f'Rank #{rank} of {total_sa3} · {band_label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── KPI row with comparison context (year + projection marker on label) ─
    k1, k2, k3 = st.columns(3)
    k1.metric(
        f"Care Gap Index ({year_used}){proj_marker}",
        f"{row['care_gap_index']:.2f}",
        f"{(row['care_gap_index'] - nat_gap):+.2f} vs national ({nat_gap:.2f})",
        delta_color="inverse",
        help=(f"State average ({state}): {state_gap:.2f}"
              + (" · 📈 = projected for 2025 (depends on ABS pop_65_plus trend)" if is_forecast else "")),
    )
    k2.metric(
        f"Quality Score ({year_used})",
        f"{row['quality_score']:.2f} ★",
        f"{(row['quality_score'] - nat_qual):+.2f} vs national ({nat_qual:.2f})",
        help=(f"State average ({state}): {state_qual:.2f}"
              + (" · 2025 quality is real (no 📈)" if is_forecast else "")),
    )
    k3.metric(
        f"Access Rate ({year_used}){proj_marker}",
        f"{row['access_rate']:.1f}%",
        f"{(row['access_rate'] - nat_acc):+.1f}% vs national ({nat_acc:.1f}%)",
        help=(f"State average ({state}): {state_acc:.1f}%"
              + (" · 📈 = projected for 2025 (depends on ABS pop_65_plus trend)" if is_forecast else "")),
    )

    # ── Mini trend charts (custom plotly, clean & light) ────────────────────
    hist = (df[df['sa3_name'] == search]
            .dropna(subset=['year'])
            .sort_values('year'))
    if len(hist) >= 2:
        years = [int(y) for y in hist['year'].tolist()]
        t1, t2, t3 = st.columns(3)
        with t1:
            if 'care_gap_index' in hist.columns:
                st.plotly_chart(
                    _mini_trend(years, hist['care_gap_index'].tolist(),
                                title='Care Gap Index trend', line_colour='#3D6FA0', value_fmt=':.2f'),
                    use_container_width=True, key='trend_gap',
                )
        with t2:
            if 'quality_score' in hist.columns:
                st.plotly_chart(
                    _mini_trend(years, hist['quality_score'].tolist(),
                                title='Quality Score trend', line_colour='#D9A53B', value_fmt=':.2f'),
                    use_container_width=True, key='trend_qual',
                )
        with t3:
            if 'access_rate' in hist.columns:
                st.plotly_chart(
                    _mini_trend(years, hist['access_rate'].tolist(),
                                title='Access Rate trend (%)', line_colour='#2BA39B', value_fmt=':.1f'),
                    use_container_width=True, key='trend_acc',
                )

    # ── Top facilities table (with org-type filter) ─────────────────────────
    _sa3_code = row.get('sa3_code')
    if _sa3_code is None or ratings is None:
        return

    _fac = ratings[ratings['sa3_code'] == _sa3_code].copy()
    if _fac.empty:
        st.caption("No facility-level data for this SA3.")
        return

    org_filter = st.selectbox(
        "Filter facilities by ownership",
        options=["All", "Not for Profit", "For Profit", "Government"],
        index=0,
        key="home_org_filter",
    )
    _filter_map = {"Not for Profit": "not_for_profit", "For Profit": "profit", "Government": "government"}
    if org_filter != "All":
        _fac = _fac[_fac['org_type'] == _filter_map[org_filter]]

    if _fac.empty:
        st.info(f"No {org_filter.lower()} facilities in this area.")
        return

    _top5 = (
        _fac.sort_values('snapshot_date')
        .groupby('Service Name', as_index=False)
        .last()
        .nlargest(5, 'quality_score')
        [['Service Name', 'Provider Name', 'org_type', 'quality_score', 'overall_rating']]
        .rename(columns={
            'Service Name': 'Facility',
            'Provider Name': 'Provider',
            'org_type': 'Type',
            'quality_score': 'Quality',
            'overall_rating': 'Stars',
        })
    )
    _top5['Quality'] = _top5['Quality'].round(2)

    rows_html = ''
    for _i, _r in enumerate(_top5.itertuples(index=False)):
        _bg = '#FFFFFF' if _i % 2 == 0 else '#FDFAF3'
        _oc = _ORG_COLOUR.get(_r.Type, '#6B7C93')
        _ol = _ORG_LABEL.get(_r.Type, _r.Type)
        rows_html += (
            f'<tr style="background:{_bg}">'
            f'<td style="padding:12px 16px;color:#11304E;font-weight:500;font-size:21px">{_r.Facility}</td>'
            f'<td style="padding:12px 16px;color:#6B7C93;font-size:20px">{_r.Provider}</td>'
            f'<td style="padding:12px 16px;font-size:20px"><span style="color:{_oc};font-weight:600">{_ol}</span></td>'
            f'<td style="padding:12px 16px;text-align:right;color:#11304E;font-weight:700;font-size:21px">{_r.Quality:.2f}</td>'
            f'<td style="padding:12px 16px;text-align:right;color:#11304E;font-size:21px">{_r.Stars:.1f} ★</td>'
            f'</tr>'
        )

    _suffix = f" · {org_filter}" if org_filter != "All" else ""
    st.markdown(
        f'<p style="margin:14px 0 8px;color:#11304E;font-weight:700;font-size:22px">'
        f'Top 5 facilities{_suffix} '
        f'<span style="font-weight:400;color:#6B7C93;font-size:19px">(latest ratings)</span></p>'
        f'<table style="width:100%;border-collapse:collapse;font-size:21px;'
        f'border:1px solid #E5DDCB;border-radius:10px;overflow:hidden">'
        f'<thead><tr style="background:#11304E">'
        f'<th style="padding:12px 16px;text-align:left;color:white;font-weight:700;font-size:20px">Facility</th>'
        f'<th style="padding:12px 16px;text-align:left;color:white;font-weight:700;font-size:20px">Provider</th>'
        f'<th style="padding:12px 16px;text-align:left;color:white;font-weight:700;font-size:20px">Type</th>'
        f'<th style="padding:12px 16px;text-align:right;color:white;font-weight:700;font-size:20px">Quality</th>'
        f'<th style="padding:12px 16px;text-align:right;color:white;font-weight:700;font-size:20px">Stars</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table>',
        unsafe_allow_html=True,
    )


def _sparkline_svg(values, *, width=140, height=32, color='#11304E') -> str:
    """Minimalist inline-SVG sparkline. Renders polyline + end-point dot.
    Returns empty string if fewer than 2 values."""
    pts = [(i, float(v)) for i, v in enumerate(values) if v is not None and v == v]
    if len(pts) < 2:
        return ''
    vmin = min(v for _, v in pts)
    vmax = max(v for _, v in pts)
    rng = (vmax - vmin) or 1.0
    n = len(pts)
    coords = []
    for i, v in pts:
        x = i * width / (n - 1)
        y = height - (v - vmin) / rng * (height - 4) - 2
        coords.append(f"{x:.1f},{y:.1f}")
    last_x, last_y = coords[-1].split(',')
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'style="display:block;margin:6px 0 0">'
        f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{last_x}" cy="{last_y}" r="3" fill="{color}"/>'
        f'</svg>'
    )


def _compute_hero_kpis(supply, population, ratings, service_users):
    """Return the 4 national hero numbers shown on the Home scoreboard.

    Independent of the sidebar filter — these are the dashboard's elevator pitch."""
    # 1. Crisis zones — latest overlap year where waitlist_pressure > 1.0
    su_yrs = set(int(y) for y in service_users['year'].dropna().unique())
    sp_yrs = set(int(y) for y in supply['year'].dropna().unique())
    common = sorted(su_yrs & sp_yrs)
    latest_yr = common[-1] if common else None
    crisis_n = 0
    if latest_yr is not None:
        su = service_users[service_users['year'] == latest_yr][['sa3_code', 'hcp_high_needs']]
        sp = supply[supply['year'] == latest_yr][['sa3_code', 'residential_places']]
        j = su.merge(sp, on='sa3_code', how='inner')
        j = j[j['residential_places'] > 0]
        crisis_n = int((j['hcp_high_needs'] / j['residential_places'] > 1.0).sum())

    # 2. Mandate Δ — after-mandate minus before-mandate mean quality_score
    known = ratings[ratings['org_type'] != 'unknown']
    before = known[known['period'] == 'Before mandate']['quality_score']
    after  = known[known['period'] == 'After mandate']['quality_score']
    mandate_delta = float(after.mean() - before.mean()) if len(before) and len(after) else 0.0

    # 3. Ownership quality gap (govt − for-profit)
    org_means = known.groupby('org_type')['quality_score'].mean()
    quality_gap = float(org_means.get('government', 0) - org_means.get('profit', 0))

    # 4. Beds per 1,000 elderly — % change 2019 → latest
    sp_pop_yrs = sorted(sp_yrs & set(int(y) for y in population['year'].dropna().unique()))
    base_yr = 2019 if 2019 in sp_pop_yrs else (sp_pop_yrs[0] if sp_pop_yrs else None)
    end_yr  = sp_pop_yrs[-1] if sp_pop_yrs else None

    def _beds_per_1k(yr):
        m = supply.merge(
            population[['sa3_code', 'year', 'pop_65_plus']],
            on=['sa3_code', 'year'], how='inner',
        )
        m = m[(m['year'] == yr) & (m['pop_65_plus'] > 0)]
        tot_beds = float(m['residential_places'].sum())
        tot_pop  = float(m['pop_65_plus'].sum())
        return (tot_beds / tot_pop * 1000) if tot_pop else 0.0

    beds_pct = 0.0
    if base_yr and end_yr and end_yr != base_yr:
        b0, b1 = _beds_per_1k(base_yr), _beds_per_1k(end_yr)
        beds_pct = ((b1 - b0) / b0 * 100) if b0 else 0.0

    # Sparkline trends — small ordered series per card
    # Crisis zones per year (2023, 2024, 2025 if available)
    crisis_trend = []
    for yr in common:
        su = service_users[service_users['year'] == yr][['sa3_code', 'hcp_high_needs']]
        sp = supply[supply['year'] == yr][['sa3_code', 'residential_places']]
        j = su.merge(sp, on='sa3_code', how='inner')
        j = j[j['residential_places'] > 0]
        crisis_trend.append(float((j['hcp_high_needs'] / j['residential_places'] > 1.0).sum()))

    # Mandate sparkline: national mean quality per snapshot, chronological
    snap_q = (
        known.dropna(subset=['snapshot_date', 'quality_score'])
        .groupby('snapshot_date')['quality_score'].mean()
        .sort_index()
    )
    mandate_trend = [float(v) for v in snap_q.values]

    # Ownership gap sparkline: per-snapshot govt-vs-profit gap
    snap_gap = (
        known.dropna(subset=['snapshot_date', 'org_type', 'quality_score'])
        .pivot_table(index='snapshot_date', columns='org_type',
                     values='quality_score', aggfunc='mean')
    )
    if 'government' in snap_gap.columns and 'profit' in snap_gap.columns:
        gap_series = (snap_gap['government'] - snap_gap['profit']).dropna()
        quality_gap_trend = [float(v) for v in gap_series.values]
    else:
        quality_gap_trend = []

    # Beds per 1k sparkline: every year base_yr → end_yr
    beds_trend = []
    if base_yr and end_yr:
        for yr in sorted(sp_pop_yrs):
            beds_trend.append(_beds_per_1k(yr))

    return {
        'crisis_n': crisis_n,
        'latest_yr': latest_yr,
        'mandate_delta': mandate_delta,
        'quality_gap': quality_gap,
        'beds_pct': beds_pct,
        'beds_base_yr': base_yr,
        'beds_end_yr': end_yr,
        'crisis_trend': crisis_trend,
        'mandate_trend': mandate_trend,
        'quality_gap_trend': quality_gap_trend,
        'beds_trend': beds_trend,
    }


def render(hero_b64: str, df, gdf, supply, population, ratings, service_users) -> None:
    # ── Condensed hero (no CTA — map is right below) ───────────────────────
    hero_style = (
        f"background:linear-gradient(rgba(27,63,110,0.60),rgba(27,63,110,0.60)),"
        f"url('data:image/jpeg;base64,{hero_b64}') center/cover no-repeat;"
        if hero_b64
        else f"background:linear-gradient(135deg,{C['navy']},{C['teal']});"
    )
    # Hero stat-led subtitle uses live national numbers (computed below for scoreboard)
    _hero_kpis = _compute_hero_kpis(supply, population, ratings, service_users)
    st.markdown(
        f'<div class="hero-wrap" role="banner" '
        f'aria-label="Australia\'s Aged Care Gap — national dashboard hero" '
        f'style="{hero_style};min-height:280px">'
        f'<div class="hero-inner">'
        f'<div class="hero-h" style="font-size:2.0rem;margin-bottom:14px">'
        f'Australia\'s Aged-Care Gap'
        f'</div>'
        f'<div style="color:white;font-size:1.35rem;opacity:0.95;max-width:780px;'
        f'margin:0 auto;font-weight:700;letter-spacing:0.01em">'
        f'<span style="color:#FFD27A">{_hero_kpis["crisis_n"]}</span> communities in crisis · '
        f'<span style="color:#FFD27A">1</span> federal mandate · '
        f'<span style="color:#FFD27A">{_hero_kpis["beds_end_yr"] - _hero_kpis["beds_base_yr"]}</span> years of decline.'
        f'</div>'
        f'<div style="color:white;font-size:0.95rem;opacity:0.78;margin-top:8px">'
        f'A live data view of quality, access, supply and demand across Australia.'
        f'</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── "Start here" CTA for first-time viewers ────────────────────────────
    st.markdown(
        f'<a href="?page=map" target="_self" style="text-decoration:none">'
        f'<div style="background:{C["white"]};border:2px solid {C["teal"]};'
        f'border-radius:12px;padding:16px 22px;margin:0 0 18px;'
        f'display:flex;justify-content:space-between;align-items:center;'
        f'transition:transform 0.15s ease, box-shadow 0.15s ease">'
        f'<div>'
        f'<div style="color:{C["muted"]};font-size:11px;letter-spacing:0.08em;'
        f'text-transform:uppercase;font-weight:700">New here? Start the story</div>'
        f'<div style="color:{C["navy"]};font-size:18px;font-weight:700;margin-top:4px">'
        f'Chapter 1: The Gap → Where the worst regions are</div>'
        f'</div>'
        f'<div style="background:{C["teal"]};color:white;padding:10px 22px;'
        f'border-radius:24px;font-weight:700;font-size:14px;white-space:nowrap">'
        f'Start →</div>'
        f'</div></a>',
        unsafe_allow_html=True,
    )

    # ── National scoreboard — 4 hero KPIs spanning all 4 chapters ──────────
    _kpis = _hero_kpis  # reuse the dict already computed for the hero subtitle
    _label_style = (
        'font-size:13px;font-weight:700;letter-spacing:0.04em;'
        'text-transform:uppercase;color:#6B7C93;margin-bottom:4px'
    )
    _foot_style = 'color:#6B7C93;font-size:14px;margin-top:6px'

    # Intro line so the 4 numbers land with context
    st.markdown(
        f'<p style="text-align:center;color:{C["slate"]};font-size:16px;'
        f'margin:18px 0 8px;font-style:italic">'
        f'Across Australia, the gap between aged-care quality and access shows up '
        f'in <b>4 numbers</b> — each links to its full chapter below.'
        f'</p>',
        unsafe_allow_html=True,
    )

    _sp_crisis  = _sparkline_svg(_kpis['crisis_trend'],     color=C['red'])
    _sp_mandate = _sparkline_svg(_kpis['mandate_trend'],    color=C['teal'])
    _sp_gap     = _sparkline_svg(_kpis['quality_gap_trend'], color=C['navy'])
    _sp_beds    = _sparkline_svg(_kpis['beds_trend'],       color=C['red'])
    st.markdown(
        f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:8px 0 18px">
  <div class="kpi-card">
    <div style="{_label_style}">🚨 Crisis Zones · {_kpis['latest_yr']}
      <span class="kpi-help" data-tooltip="SA3 regions where high-needs home-care users exceed available residential beds (waitlist pressure &gt; 1.0)">?</span>
    </div>
    <div class="kpi-value" style="color:{C['red']}">{_kpis['crisis_n']}</div>
    {_sp_crisis}
    <div style="{_foot_style}">SA3 with waitlist &gt; 1.0
      <a href="?page=reveal" target="_self" style="color:{C['teal']};text-decoration:none">→ Ch3</a>
    </div>
  </div>
  <div class="kpi-card">
    <div style="{_label_style}">⚖️ Mandate Quality Δ
      <span class="kpi-help" data-tooltip="National avg quality score after the Oct 2023 staffing mandate minus before. Positive = mandate improved care.">?</span>
    </div>
    <div class="kpi-value" style="color:{C['teal']}">{_kpis['mandate_delta']:+.2f}<span class="kpi-suffix"> ★</span></div>
    {_sp_mandate}
    <div style="{_foot_style}">Post-Oct 2023 nat. avg
      <a href="?page=mandate" target="_self" style="color:{C['teal']};text-decoration:none">→ Ch4</a>
    </div>
  </div>
  <div class="kpi-card">
    <div style="{_label_style}">🏢 Govt vs For-Profit Gap
      <span class="kpi-help" data-tooltip="Mean quality star rating for government-run facilities minus for-profit facilities (national, all snapshots)">?</span>
    </div>
    <div class="kpi-value">{_kpis['quality_gap']:.2f}<span class="kpi-suffix"> pts</span></div>
    {_sp_gap}
    <div style="{_foot_style}">Quality star gap
      <a href="?page=correlation" target="_self" style="color:{C['teal']};text-decoration:none">→ Ch2</a>
    </div>
  </div>
  <div class="kpi-card">
    <div style="{_label_style}">🛏️ Beds per 1k · {_kpis['beds_base_yr']}→{_kpis['beds_end_yr']}
      <span class="kpi-help" data-tooltip="% change in residential beds per 1,000 people aged 65+ from base year to latest. Negative = supply shrinking.">?</span>
    </div>
    <div class="kpi-value" style="color:{C['red']}">{_kpis['beds_pct']:+.1f}<span class="kpi-suffix"> %</span></div>
    {_sp_beds}
    <div style="{_foot_style}">Residential supply per 65+
      <a href="?page=map" target="_self" style="color:{C['teal']};text-decoration:none">→ Ch1</a>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # ── Map + Find My Area as sub-tabs ─────────────────────────────────────
    tab_map, tab_find = st.tabs([
        "🗺️ Interactive Map",
        "🔍 Find My Area",
    ])
    with tab_map:
        pg_fullmap.render(df, gdf, supply, population, service_users=service_users,
                          ratings=ratings, show_movement=True)
    with tab_find:
        st.markdown(
            '<p style="color:#4A5A6E;font-size:20px;margin:0 0 12px;line-height:1.6">'
            'Search for an SA3 region to see its Care Gap Index, Quality, Access Rate, '
            'remoteness band, and the top 5 facilities by quality.</p>',
            unsafe_allow_html=True,
        )
        _render_find_my_area(df, ratings, supply=supply, population=population,
                             service_users=service_users)

    st.markdown(
        '<p class="data-caption">Data compiled from Aged Care Official Website &amp; ABS 2019–2026</p>',
        unsafe_allow_html=True,
    )
