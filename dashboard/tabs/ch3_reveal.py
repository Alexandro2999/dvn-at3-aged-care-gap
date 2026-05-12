import pandas as pd
import streamlit as st
import plotly.express as px
from tabs.utils import C, theme

HCP_COLS = ['hcp_level1', 'hcp_level2', 'hcp_level3', 'hcp_level4']
LEVEL_LABELS = {
    'hcp_level1': 'L1 — Basic',
    'hcp_level2': 'L2 — Moderate',
    'hcp_level3': 'L3 — High',
    'hcp_level4': 'L4 — Very High (should be residential)',
}
LEVEL_ORDER = ['L1 — Basic', 'L2 — Moderate', 'L3 — High',
               'L4 — Very High (should be residential)']
LEVEL_COLOURS = {
    'L1 — Basic':                              '#A6C8FF',
    'L2 — Moderate':                           '#4589FF',
    'L3 — High':                               C['gold'],
    'L4 — Very High (should be residential)':  C['red'],
}


def _build_year_frame(meta_df, service_users, supply, year):
    """Build SA3 frame for `year` with hcp + supply + state/MMM meta inner-joined.
    meta_df is the filtered master frame (carries sidebar state/MMM filter)."""
    meta = meta_df[['sa3_code', 'sa3_name', 'state', 'mmm_code']].drop_duplicates('sa3_code')
    su_yr = service_users[service_users['year'] == year].copy()
    sup_yr = supply[supply['year'] == year][['sa3_code', 'residential_places']]
    df = (
        su_yr
        .merge(sup_yr, on='sa3_code', how='inner')
        .merge(meta[['sa3_code', 'state', 'mmm_code']], on='sa3_code', how='inner')
    )
    df = df[df['residential_places'] > 0].copy()
    df['waitlist_pressure'] = df['hcp_high_needs'] / df['residential_places']
    return df


def _hcp_donut(row_like, *, title, height=320):
    """Render a donut for a single row of HCP counts."""
    counts = [int(row_like.get(c, 0) or 0) for c in HCP_COLS]
    pie_df = pd.DataFrame({
        'level_label': [LEVEL_LABELS[c] for c in HCP_COLS],
        'users': counts,
    })
    fig = px.pie(
        pie_df,
        names='level_label', values='users',
        category_orders={'level_label': LEVEL_ORDER},
        color='level_label', color_discrete_map=LEVEL_COLOURS,
        title=title,
        hole=0.5,
    )
    fig.update_traces(
        textposition='inside', textinfo='percent',
        hovertemplate='%{label}<br>%{value:,d} users (%{percent})<extra></extra>',
    )
    theme(fig, height=height)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Section A — System shift (3 donuts national)
# ─────────────────────────────────────────────────────────────────────────────
def _render_section_a(service_users):
    st.markdown(
        '<div class="sub-h">How is the system shifting? National HCP mix</div>',
        unsafe_allow_html=True,
    )

    nat = (
        service_users.groupby('year')[HCP_COLS]
        .sum().reset_index().sort_values('year')
    )
    nat_yrs = sorted(int(y) for y in nat['year'].unique())
    if not nat_yrs:
        st.info("No national HCP data available.")
        return

    cols = st.columns(len(nat_yrs))
    for col, yr in zip(cols, nat_yrs):
        row = nat[nat['year'] == yr].iloc[0]
        fig_pie = _hcp_donut(row, title=f'National HCP mix — {yr}', height=300)
        fig_pie.update_layout(
            showlegend=bool(yr == nat_yrs[-1]),
            legend=dict(orientation='v', yanchor='middle', y=0.5),
        )
        col.plotly_chart(fig_pie, use_container_width=True)

    if len(nat_yrs) >= 2:
        y0, y_end = nat_yrs[0], nat_yrs[-1]
        r0 = nat[nat['year'] == y0].iloc[0]
        r1 = nat[nat['year'] == y_end].iloc[0]
        tot0 = int(r0[HCP_COLS].sum())
        tot1 = int(r1[HCP_COLS].sum())
        l34_0 = (r0['hcp_level3'] + r0['hcp_level4']) / tot0 * 100 if tot0 else 0
        l34_1 = (r1['hcp_level3'] + r1['hcp_level4']) / tot1 * 100 if tot1 else 0
        total_growth = (tot1 / tot0 - 1) * 100 if tot0 else 0
        l4_growth = (r1['hcp_level4'] / r0['hcp_level4'] - 1) * 100 if r0['hcp_level4'] else 0
        st.warning(
            f"⚠️ Between **{y0}** and **{y_end}**, total home-care users grew "
            f"**{total_growth:+.0f}%** ({tot0:,} → {tot1:,}). "
            f"The **L4 (very-high needs) cohort grew {l4_growth:+.0f}%** "
            f"({int(r0['hcp_level4']):,} → {int(r1['hcp_level4']):,}). "
            f"L3+L4 share moved from **{l34_0:.1f}% → {l34_1:.1f}%** — "
            f"the system is getting heavier-needs, not lighter."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Section B — Top 10 SA3 + year toggle + click drill-down
# ─────────────────────────────────────────────────────────────────────────────
def _render_section_b(df, service_users, supply):
    su_yrs = set(int(y) for y in service_users['year'].dropna().unique())
    sp_yrs = set(int(y) for y in supply['year'].dropna().unique())
    yrs_available = sorted(y for y in (su_yrs & sp_yrs) if y >= 2023)

    if not yrs_available:
        st.info("No overlapping years between service_users and supply.")
        return

    year_sel = st.radio(
        "Year",
        options=yrs_available,
        index=len(yrs_available) - 1,
        horizontal=True,
        key="ch3_year",
    )

    df_yr = _build_year_frame(df, service_users, supply, year_sel)
    if df_yr.empty:
        st.info(f"No SA3 data for {year_sel} under the current filter.")
        return

    n_deficit_yr = int((df_yr.drop_duplicates('sa3_name')['waitlist_pressure'] > 1.0).sum())
    worst = df_yr.drop_duplicates('sa3_name').nlargest(1, 'waitlist_pressure').iloc[0]
    st.markdown(
        f'<p class="sec-p">In <b>{year_sel}</b>, '
        f'<b>{n_deficit_yr} SA3 regions</b> have more high-needs home-care users '
        f'than available residential beds. The worst is '
        f'<b>{worst["sa3_name"]} ({worst["state"]})</b> with a pressure ratio of '
        f'<b>{worst["waitlist_pressure"]:.2f}</b> — '
        f'{int(worst["hcp_high_needs"]):,} high-needs people competing for '
        f'{int(worst["residential_places"]):,} beds.</p>',
        unsafe_allow_html=True,
    )

    top10 = (
        df_yr.nlargest(15, 'waitlist_pressure')
        .drop_duplicates('sa3_name').head(10)
        .sort_values('waitlist_pressure').copy()
    )
    if top10.empty:
        st.info(f"No SA3s with positive waitlist pressure in {year_sel}.")
        return

    q75 = top10['waitlist_pressure'].quantile(0.75)
    top10['colour'] = top10['waitlist_pressure'].apply(
        lambda x: C['red'] if x >= q75 else C['navy']
    )
    top10['row_label'] = top10['sa3_name'] + ' (' + top10['state'] + ')'

    st.caption("↓ Click any bar to see that SA3's HCP breakdown ↓")
    fig_wp = px.bar(
        top10,
        x='waitlist_pressure', y='row_label', orientation='h',
        color='colour', color_discrete_map='identity',
        text='waitlist_pressure',
        custom_data=['sa3_code', 'sa3_name', 'state',
                     'hcp_level1', 'hcp_level2', 'hcp_level3', 'hcp_level4',
                     'hcp_high_needs', 'residential_places'],
        title=f'Top 10 SA3 Regions by Waitlist Pressure ({year_sel})<br>'
              '<sup>Red = top quartile (highest pressure)</sup>',
        labels={'waitlist_pressure': 'Waitlist Pressure Index', 'row_label': ''},
    )
    fig_wp.update_traces(
        texttemplate='%{text:.3f}', textposition='outside',
        hovertemplate=(
            '<b>%{customdata[1]} (%{customdata[2]})</b><br>'
            'Waitlist pressure: %{x:.3f}<br>'
            'High-needs users: %{customdata[7]:,d}<br>'
            'Residential beds: %{customdata[8]:,d}<extra></extra>'
        ),
    )
    fig_wp.add_vline(x=1.0, line_dash='dash', line_color=C['red'], line_width=1.5,
                     annotation_text='Demand = Supply',
                     annotation_position='top right')
    fig_wp.update_layout(showlegend=False)
    theme(fig_wp, height=400)

    event = st.plotly_chart(
        fig_wp,
        use_container_width=True,
        on_select='rerun',
        selection_mode='points',
        key=f'ch3_wp_bar_{year_sel}',
    )

    # Determine drill-down target
    selected_label = None
    selected_row = None
    try:
        pts = event.selection.get('points') if event and getattr(event, 'selection', None) else None
    except Exception:
        pts = None

    if pts:
        pt = pts[0]
        cd = pt.get('customdata') if isinstance(pt, dict) else None
        if cd and len(cd) >= 9:
            selected_label = f'{cd[1]} ({cd[2]})'
            selected_row = {
                'hcp_level1': cd[3],
                'hcp_level2': cd[4],
                'hcp_level3': cd[5],
                'hcp_level4': cd[6],
            }

    # National baseline for the chosen year
    nat = (
        service_users[service_users['year'] == year_sel]
        .groupby('year')[HCP_COLS].sum().reset_index()
    )

    st.markdown("---")
    if selected_row is not None:
        st.markdown(
            f'<div class="sub-h">HCP breakdown — {selected_label} ({year_sel})</div>',
            unsafe_allow_html=True,
        )
        row_for_donut = selected_row
        sub_label = selected_label
    else:
        st.markdown(
            f'<div class="sub-h">HCP breakdown — National average ({year_sel}) '
            '<span style="font-size:0.65em;color:#666">'
            '— click any bar above to drill into one SA3</span></div>',
            unsafe_allow_html=True,
        )
        if not nat.empty:
            nat_row = nat.iloc[0]
            row_for_donut = {c: int(nat_row[c]) for c in HCP_COLS}
        else:
            row_for_donut = {c: 0 for c in HCP_COLS}
        sub_label = 'National'

    d_col, k_col = st.columns([1.2, 1])
    with d_col:
        fig_drill = _hcp_donut(row_for_donut, title=f'{sub_label} — HCP mix', height=360)
        fig_drill.update_layout(showlegend=False)
        st.plotly_chart(fig_drill, use_container_width=True)

    with k_col:
        total = sum(row_for_donut[c] for c in HCP_COLS)
        for c in HCP_COLS:
            cnt = int(row_for_donut[c])
            pct = (cnt / total * 100) if total else 0
            st.metric(LEVEL_LABELS[c], f'{cnt:,d}', f'{pct:.1f}% of total')
        st.metric('Total home-care users', f'{int(total):,d}')


# ─────────────────────────────────────────────────────────────────────────────
# Section C — ACPR demographic drill-down
# ─────────────────────────────────────────────────────────────────────────────
def _render_section_c(acpr_res, acpr_hc):
    acpr_yrs_res = sorted(acpr_res['year'].dropna().unique().astype(int).tolist())
    acpr_yrs_hc  = sorted(acpr_hc['year'].dropna().unique().astype(int).tolist())
    # Exclude 2019 — GEN 2019 lacks sex/indigenous/age breakdowns
    acpr_yrs = sorted(y for y in set(acpr_yrs_res) & set(acpr_yrs_hc) if y >= 2020)
    if not acpr_yrs:
        st.info("ACPR data not available.")
        return

    col_yr, _ = st.columns([1, 4])
    with col_yr:
        acpr_year = st.selectbox(
            "ACPR year", options=acpr_yrs, index=len(acpr_yrs) - 1, key="acpr_year",
        )

    st.warning(
        "⚠️ **Different geographic grain**: this section is at **ACPR level (73 regions)** — "
        "demographic dimensions (Indigenous, HCP composition) are not available at SA3 level. "
        "Sidebar **state / MMM filters do not apply** to these two charts."
    )

    res_y = acpr_res[(acpr_res['year'] == acpr_year) & (acpr_res['total_users'] > 0)].copy()
    res_y['indigenous_pct'] = res_y['n_indigenous'] / res_y['total_users'] * 100
    res_y['acpr_label'] = res_y['acpr_name'] + ' (' + res_y['state'] + ')'
    top_indig = (
        res_y.nlargest(10, 'indigenous_pct')
        .sort_values('indigenous_pct')
        [['acpr_label', 'state', 'indigenous_pct', 'total_users', 'n_indigenous']]
    )

    hc_y = acpr_hc[(acpr_hc['year'] == acpr_year) & (acpr_hc['total_users'] > 0)].copy()
    hc_y['hcp_high_needs'] = hc_y[['hcp_l3', 'hcp_l4']].sum(axis=1)
    hc_y['hcp_high_pct'] = hc_y['hcp_high_needs'] / hc_y['total_users'] * 100
    hc_y['acpr_label'] = hc_y['acpr_name'] + ' (' + hc_y['state'] + ')'
    top_hcp = (
        hc_y.nlargest(10, 'hcp_high_pct')
        .sort_values('hcp_high_pct')
        [['acpr_label', 'state', 'hcp_high_pct', 'total_users', 'hcp_high_needs']]
    )

    c1, c2 = st.columns(2)
    with c1:
        fig_indig = px.bar(
            top_indig,
            x='indigenous_pct', y='acpr_label', orientation='h',
            color_discrete_sequence=[C['gold']],
            text='indigenous_pct',
            hover_data={
                'state': True, 'total_users': ':,d',
                'n_indigenous': ':,d', 'indigenous_pct': ':.1f',
                'acpr_label': False,
            },
            title=f'Top 10 ACPRs — Indigenous share of residential users ({acpr_year})',
            labels={'indigenous_pct': 'Indigenous %', 'acpr_label': ''},
        )
        fig_indig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        theme(fig_indig, height=420)
        st.plotly_chart(fig_indig, use_container_width=True)

    with c2:
        fig_hcp = px.bar(
            top_hcp,
            x='hcp_high_pct', y='acpr_label', orientation='h',
            color_discrete_sequence=[C['red']],
            text='hcp_high_pct',
            hover_data={
                'state': True, 'total_users': ':,d',
                'hcp_high_needs': ':,d', 'hcp_high_pct': ':.1f',
                'acpr_label': False,
            },
            title=f'Top 10 ACPRs — HCP high-needs (L3+L4) share of home-care users ({acpr_year})',
            labels={'hcp_high_pct': 'HCP L3+L4 %', 'acpr_label': ''},
        )
        fig_hcp.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        theme(fig_hcp, height=420)
        st.plotly_chart(fig_hcp, use_container_width=True)

    top15_indig = set(res_y.nlargest(15, 'indigenous_pct')['acpr_label'])
    top15_hcp   = set(hc_y.nlargest(15, 'hcp_high_pct')['acpr_label'])
    both = sorted(top15_indig & top15_hcp)

    if both:
        names = ", ".join(both)
        st.info(
            f"💡 **{len(both)} ACPR regions** appear in BOTH the top-15 Indigenous-share "
            f"and top-15 HCP-high-needs lists ({acpr_year}): **{names}**. "
            f"These are **double-burden communities** — high Indigenous concentration "
            f"AND high-needs care demand."
        )
    else:
        st.info(
            f"No ACPR region appears in BOTH top-15 Indigenous-share and "
            f"top-15 HCP-high-needs lists in {acpr_year}."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────
def render(df, supply, n_deficit: int, acpr_res=None, acpr_hc=None, service_users=None) -> None:
    st.markdown(
        '<div class="sec-h1">Which communities are being left behind?</div>',
        unsafe_allow_html=True,
    )

    if df.empty or service_users is None or service_users.empty:
        st.warning("No data for the current filter selection.")
        return

    tab_a, tab_b, tab_c = st.tabs([
        "🧭 System shift (national)",
        "📍 Worst SA3 + drill-down",
        "👥 ACPR demographics",
    ])

    with tab_a:
        _render_section_a(service_users)
    with tab_b:
        _render_section_b(df, service_users, supply)
    with tab_c:
        if acpr_res is not None and acpr_hc is not None:
            _render_section_c(acpr_res, acpr_hc)
        else:
            st.info("ACPR data not loaded.")
