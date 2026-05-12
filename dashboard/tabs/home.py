import streamlit as st

from tabs.utils import C, SCENARIO_GROWTH_RATES
import tabs.fullmap as pg_fullmap
from tabs.fullmap import (
    _METRIC_DEFS,
    _build_waitlist_frame,
    _project_df_to_2025,
    _movement_kpis,
)


MMM_LABELS = {
    'MM1': 'Major City', 'MM2': 'Inner Regional', 'MM3': 'Outer Regional',
    'MM4': 'Remote', 'MM5': 'Small Rural', 'MM6': 'Remote Community', 'MM7': 'Very Remote',
}


AUDIENCE_CARDS_HTML = f"""
<div style="margin: 32px 0 16px; text-align:center;
            color:{C['navy']}; font-weight:700; font-size:1.1rem;">
    Pick your story
</div>
<div style="display:grid; grid-template-columns: repeat(3, 1fr);
            gap: 18px; margin-bottom: 28px;">

  <a href="?page=map" target="_self" style="text-decoration:none;">
    <div style="background:{C['white']}; border:1.5px solid {C['border']};
                border-radius: 14px; padding: 22px 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                transition: transform 0.15s, box-shadow 0.15s;
                cursor: pointer; min-height: 170px;">
      <div style="font-size:1.6rem; margin-bottom:6px;">👨‍👩‍👧</div>
      <div style="color:{C['navy']}; font-weight:800;
                  font-size:1.0rem; margin-bottom:6px;">Families</div>
      <div style="color:{C['muted']}; font-size:0.82rem; line-height:1.45;">
        Is care near my family any good?<br>
        See state &amp; remoteness patterns.
      </div>
      <div style="color:{C['teal']}; font-weight:700; font-size:0.8rem;
                  margin-top:14px;">→ Chapter 1: The Map</div>
    </div>
  </a>

  <a href="?page=forecast" target="_self" style="text-decoration:none;">
    <div style="background:{C['white']}; border:1.5px solid {C['border']};
                border-radius: 14px; padding: 22px 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                cursor: pointer; min-height: 170px;">
      <div style="font-size:1.6rem; margin-bottom:6px;">💼</div>
      <div style="color:{C['navy']}; font-weight:800;
                  font-size:1.0rem; margin-bottom:6px;">Workers</div>
      <div style="color:{C['muted']}; font-size:0.82rem; line-height:1.45;">
        Where are workers most needed?<br>
        See where supply is collapsing.
      </div>
      <div style="color:{C['teal']}; font-weight:700; font-size:0.8rem;
                  margin-top:14px;">→ Chapter 5: The Forecast</div>
    </div>
  </a>

  <a href="?page=correlation" target="_self" style="text-decoration:none;">
    <div style="background:{C['white']}; border:1.5px solid {C['border']};
                border-radius: 14px; padding: 22px 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                cursor: pointer; min-height: 170px;">
      <div style="font-size:1.6rem; margin-bottom:6px;">📊</div>
      <div style="color:{C['navy']}; font-weight:800;
                  font-size:1.0rem; margin-bottom:6px;">Investors</div>
      <div style="color:{C['muted']}; font-size:0.82rem; line-height:1.45;">
        Where are the market gaps?<br>
        See ownership &amp; funding patterns.
      </div>
      <div style="color:{C['teal']}; font-weight:700; font-size:0.8rem;
                  margin-top:14px;">→ Chapter 2: The Why</div>
    </div>
  </a>

</div>
"""


def _render_movement_top(df, supply, service_users, ratings, population):
    """Render 2024→2025 movement KPIs at top of Home — reads session_state for
    metric/year/scenario picked in the Map tab below. First load uses defaults."""
    scenario = st.session_state.get('fm_scenario', list(SCENARIO_GROWTH_RATES.keys())[0])
    df_proj = _project_df_to_2025(df, supply, service_users, ratings, population, scenario)

    metric_label_to_def = {m[0]: m for m in _METRIC_DEFS}
    default_metric_label = _METRIC_DEFS[0][0]
    metric_label = st.session_state.get('fm_metric', default_metric_label)
    if metric_label not in metric_label_to_def:
        metric_label = default_metric_label
    _, col_c, _, _, src_c, higher_is_better, _ = metric_label_to_def[metric_label]

    wp_frame = _build_waitlist_frame(service_users, supply)
    _df_years = sorted(df_proj['year'].dropna().unique().tolist())
    _sup_years = sorted(supply['year'].dropna().unique().tolist())
    _pop_years = sorted(population['year'].dropna().unique().tolist())
    _beds_years = sorted(set(_sup_years) & set(_pop_years))
    if 2025 in _df_years and 2025 not in _beds_years:
        _beds_years = sorted(_beds_years + [2025])
    _wp_years = sorted(int(y) for y in wp_frame['year'].dropna().unique()) if not wp_frame.empty else _df_years
    _YEAR_MAP = {'df': _df_years, 'waitlist': _wp_years, 'supply': _beds_years, 'supply_nopop': _sup_years}

    avail_years = [int(y) for y in _YEAR_MAP[src_c]]
    if not avail_years:
        return
    year_default = avail_years[-1]
    year_c = st.session_state.get('fm_year', year_default)
    if year_c not in avail_years:
        year_c = year_default
    year_prev = year_c - 1
    if year_prev not in avail_years:
        st.info(
            f"Movement data not available — no {metric_label} data for {year_prev}. "
            f"Pick a later year in the Map tab to see year-on-year changes."
        )
        return

    sa3_meta = df_proj[['sa3_code', 'sa3_name', 'state', 'mmm_code']].drop_duplicates('sa3_code')
    _movement_kpis(
        col_c, src_c, higher_is_better, metric_label,
        year_c, year_prev, df_proj, supply, population, sa3_meta,
        wp_frame=wp_frame,
    )


def _render_find_my_area(df, ratings):
    """SA3 search → detail card + top-5 facilities (mirrors ch1_map Tab C logic)."""
    if df is None or df.empty:
        st.info("No SA3 data available for Find My Area.")
        return

    latest_year = int(df['year'].max())
    df_yr = df[df['year'] == latest_year].drop_duplicates('sa3_name').copy()
    _sa3_opts = [""] + sorted(df_yr['sa3_name'].dropna().unique().tolist())

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
    st.markdown(
        f'<div class="nb-card">'
        f'<b>{search}</b> ({row.get("state", "")})'
        f'&nbsp;&nbsp;·&nbsp;&nbsp;Care Gap: <b>{row["care_gap_index"]:.2f}</b>'
        f'&nbsp;&nbsp;·&nbsp;&nbsp;Quality: <b>{row["quality_score"]:.2f}★</b>'
        f'&nbsp;&nbsp;·&nbsp;&nbsp;Access Rate: <b>{row["access_rate"]:.1f}%</b>'
        f'&nbsp;&nbsp;·&nbsp;&nbsp;Remoteness: <b>{MMM_LABELS.get(row.get("mmm_code", ""), row.get("mmm_code", ""))}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )

    _sa3_code = row.get('sa3_code')
    if _sa3_code is None or ratings is None:
        return

    _fac = ratings[ratings['sa3_code'] == _sa3_code].copy()
    if _fac.empty:
        st.caption("No facility-level data for this SA3.")
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
    _org_colour = {'profit': '#D94F3D', 'not_for_profit': '#1B3F6E', 'government': '#00A79D'}
    _org_label = {'profit': 'For Profit', 'not_for_profit': 'Not for Profit', 'government': 'Government'}

    rows_html = ''
    for _i, _r in enumerate(_top5.itertuples(index=False)):
        _bg = '#FFFFFF' if _i % 2 == 0 else '#F3F9FE'
        _oc = _org_colour.get(_r.Type, '#6B7C93')
        _ol = _org_label.get(_r.Type, _r.Type)
        rows_html += (
            f'<tr style="background:{_bg}">'
            f'<td style="padding:12px 16px;color:#1B3F6E;font-weight:500;font-size:16px">{_r.Facility}</td>'
            f'<td style="padding:12px 16px;color:#6B7C93;font-size:15px">{_r.Provider}</td>'
            f'<td style="padding:12px 16px;font-size:15px"><span style="color:{_oc};font-weight:600">{_ol}</span></td>'
            f'<td style="padding:12px 16px;text-align:right;color:#1B3F6E;font-weight:700;font-size:16px">{_r.Quality:.2f}</td>'
            f'<td style="padding:12px 16px;text-align:right;color:#1B3F6E;font-size:16px">{_r.Stars:.1f} ★</td>'
            f'</tr>'
        )

    st.markdown(
        f'<p style="margin:16px 0 8px;color:#1B3F6E;font-weight:700;font-size:17px">'
        f'Top 5 facilities in this area <span style="font-weight:400;color:#6B7C93;font-size:14px">(latest ratings)</span></p>'
        f'<table style="width:100%;border-collapse:collapse;font-size:16px;'
        f'border:1px solid #C8DCF0;border-radius:10px;overflow:hidden">'
        f'<thead><tr style="background:#1B3F6E">'
        f'<th style="padding:12px 16px;text-align:left;color:white;font-weight:700;font-size:16px">Facility</th>'
        f'<th style="padding:12px 16px;text-align:left;color:white;font-weight:700;font-size:16px">Provider</th>'
        f'<th style="padding:12px 16px;text-align:left;color:white;font-weight:700;font-size:16px">Type</th>'
        f'<th style="padding:12px 16px;text-align:right;color:white;font-weight:700;font-size:16px">Quality</th>'
        f'<th style="padding:12px 16px;text-align:right;color:white;font-weight:700;font-size:16px">Stars</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table>',
        unsafe_allow_html=True,
    )


def render(hero_b64: str, KPI_HTML: str, df, gdf, supply, population, ratings, service_users) -> None:
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

    # ── Movement KPIs at top (replaces the static 4-card grid) ────────────
    _render_movement_top(df, supply, service_users, ratings, population)

    # ── Glossary expander ──────────────────────────────────────────────────
    with st.expander("📖 Glossary — key terms on this page", expanded=False):
        st.markdown(
            f'<div style="color:{C["navy"]};font-size:14px;line-height:1.7">'
            f'<ul style="margin:0;padding-left:22px">'
            f'<li><b>Care Gap Index</b> = residential access rate ÷ quality score. '
            f'Higher value = more underserved (high demand vs low quality).</li>'
            f'<li><b>Quality Score</b> = mean of 4 ACQSC sub-ratings '
            f'(residents experience, staffing, compliance, quality measures).</li>'
            f'<li><b>Residential Access Rate</b> = % of population aged 65+ '
            f'using residential aged care.</li>'
            f'<li><b>Waitlist Pressure</b> = high-needs HCP users ÷ residential beds (per SA3). '
            f'Values &gt; 1.0 = crisis zone where demand outpaces supply.</li>'
            f'<li><b>Beds per 1,000 elderly</b> = residential places ÷ pop 65+ × 1,000.</li>'
            f'<li><b>SA3</b> = Statistical Area Level 3, ~331 regions in Australia (ABS).</li>'
            f'<li><b>★ on Year 2025</b> = value <b>projected</b> from ABS Baseline trend '
            f'(or selected scenario). Real 2025 data is used where available '
            f'(Waitlist Pressure, Number of Facilities).</li>'
            f'</ul></div>',
            unsafe_allow_html=True,
        )

    # ── Map + Find My Area as sub-tabs ─────────────────────────────────────
    tab_map, tab_find = st.tabs([
        "🗺️ Interactive Map",
        "🔍 Find My Area",
    ])
    with tab_map:
        pg_fullmap.render(df, gdf, supply, population, service_users=service_users,
                          ratings=ratings, show_movement=False)
    with tab_find:
        st.markdown(
            '<p style="color:#3D4F63;font-size:14px;margin:0 0 12px;line-height:1.6">'
            'Search for an SA3 region to see its Care Gap Index, Quality, Access Rate, '
            'remoteness band, and the top 5 facilities by quality.</p>',
            unsafe_allow_html=True,
        )
        _render_find_my_area(df, ratings)

    # ── Persona routing (demoted to bottom) ────────────────────────────────
    st.markdown("---")
    st.markdown(AUDIENCE_CARDS_HTML, unsafe_allow_html=True)

    st.markdown(
        '<p class="data-caption">Data compiled from Aged Care Official Website &amp; ABS 2019–2026</p>',
        unsafe_allow_html=True,
    )
