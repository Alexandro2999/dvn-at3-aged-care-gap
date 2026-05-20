import streamlit as st
import plotly.graph_objects as go

from tabs.utils import C, SCENARIO_GROWTH_RATES
import tabs.fullmap as pg_fullmap
from tabs.fullmap import _project_df_to_2025


MMM_LABELS = {
    'MM1': 'Major City', 'MM2': 'Inner Regional', 'MM3': 'Outer Regional',
    'MM4': 'Remote', 'MM5': 'Small Rural', 'MM6': 'Remote Community', 'MM7': 'Very Remote',
}


_ORG_COLOUR = {'profit': '#D94F3D', 'not_for_profit': '#1B3F6E', 'government': '#00A79D'}
_ORG_LABEL  = {'profit': 'For Profit', 'not_for_profit': 'Not for Profit', 'government': 'Government'}


def _mini_trend(years, values, title, line_colour='#1B3F6E', value_fmt=':.2f'):
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
        title=dict(text=title, x=0, font=dict(size=16, color='#1B3F6E', family='Inter')),
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
        return "Top 25% (better than most)", "#00A79D"
    if pct <= 0.75:
        return "Middle 50%", "#F5A623"
    return "Bottom 25% (worse than most)", "#D94F3D"


def _render_find_my_area(df, ratings, supply=None, population=None, service_users=None):
    """SA3 search → KPI cards with comparison context, crisis warning,
    trend mini-charts, and filterable top facilities table."""
    if df is None or df.empty:
        st.info("No SA3 data available for Find My Area.")
        return

    # Project df to include 2025 row (idempotent if 2025 already present)
    if supply is not None and population is not None and service_users is not None:
        scenario = st.session_state.get('fm_scenario', list(SCENARIO_GROWTH_RATES.keys())[0])
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
            f'<div style="background:#FDECEA;border-left:5px solid #D94F3D;'
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
                                title='Care Gap Index trend', line_colour='#4A7FC1', value_fmt=':.2f'),
                    use_container_width=True, key='trend_gap',
                )
        with t2:
            if 'quality_score' in hist.columns:
                st.plotly_chart(
                    _mini_trend(years, hist['quality_score'].tolist(),
                                title='Quality Score trend', line_colour='#F5A623', value_fmt=':.2f'),
                    use_container_width=True, key='trend_qual',
                )
        with t3:
            if 'access_rate' in hist.columns:
                st.plotly_chart(
                    _mini_trend(years, hist['access_rate'].tolist(),
                                title='Access Rate trend (%)', line_colour='#4CAF50', value_fmt=':.1f'),
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
        _bg = '#FFFFFF' if _i % 2 == 0 else '#F3F9FE'
        _oc = _ORG_COLOUR.get(_r.Type, '#6B7C93')
        _ol = _ORG_LABEL.get(_r.Type, _r.Type)
        rows_html += (
            f'<tr style="background:{_bg}">'
            f'<td style="padding:12px 16px;color:#1B3F6E;font-weight:500;font-size:21px">{_r.Facility}</td>'
            f'<td style="padding:12px 16px;color:#6B7C93;font-size:20px">{_r.Provider}</td>'
            f'<td style="padding:12px 16px;font-size:20px"><span style="color:{_oc};font-weight:600">{_ol}</span></td>'
            f'<td style="padding:12px 16px;text-align:right;color:#1B3F6E;font-weight:700;font-size:21px">{_r.Quality:.2f}</td>'
            f'<td style="padding:12px 16px;text-align:right;color:#1B3F6E;font-size:21px">{_r.Stars:.1f} ★</td>'
            f'</tr>'
        )

    _suffix = f" · {org_filter}" if org_filter != "All" else ""
    st.markdown(
        f'<p style="margin:14px 0 8px;color:#1B3F6E;font-weight:700;font-size:22px">'
        f'Top 5 facilities{_suffix} '
        f'<span style="font-weight:400;color:#6B7C93;font-size:19px">(latest ratings)</span></p>'
        f'<table style="width:100%;border-collapse:collapse;font-size:21px;'
        f'border:1px solid #C8DCF0;border-radius:10px;overflow:hidden">'
        f'<thead><tr style="background:#1B3F6E">'
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


def render(hero_b64: str, df, gdf, supply, population, ratings, service_users) -> None:
    # ── Condensed hero (no CTA — map is right below) ───────────────────────
    hero_style = (
        f"background:linear-gradient(rgba(27,63,110,0.60),rgba(27,63,110,0.60)),"
        f"url('data:image/jpeg;base64,{hero_b64}') center/cover no-repeat;"
        if hero_b64
        else f"background:linear-gradient(135deg,{C['navy']},{C['teal']});"
    )
    st.markdown(
        f'<div class="hero-wrap" style="{hero_style};min-height:280px">'
        f'<div class="hero-inner">'
        f'<div class="hero-h" style="font-size:2.0rem;margin-bottom:12px">'
        f'Australia\'s Aged-Care Gap'
        f'</div>'
        f'<div style="color:white;font-size:1.05rem;opacity:0.92;max-width:780px;margin:0 auto">'
        f'A live overview of quality, access, supply and demand — '
        f'with 2025 outlook projected from ABS trends.'
        f'</div>'
        f'</div></div>',
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
            '<p style="color:#3D4F63;font-size:20px;margin:0 0 12px;line-height:1.6">'
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
