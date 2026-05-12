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


def _deficit_set(service_users, supply, year):
    """Return set of SA3 codes where waitlist_pressure > 1.0 in given year.
    National scope — does not apply sidebar filter."""
    su = service_users[service_users['year'] == year][['sa3_code', 'hcp_high_needs']]
    sp = supply[supply['year'] == year][['sa3_code', 'residential_places']]
    j = su.merge(sp, on='sa3_code', how='inner')
    j = j[j['residential_places'] > 0].copy()
    j['wp'] = j['hcp_high_needs'] / j['residential_places']
    return set(j[j['wp'] > 1.0]['sa3_code'].tolist())


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
# Section: National shift (3 donuts national HCP mix)
# ─────────────────────────────────────────────────────────────────────────────
def _render_section_national(service_users):
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
# Section: Crisis zones MERGED — counter cards + bar+drill + crisis-vs-rest line
# ─────────────────────────────────────────────────────────────────────────────
def _render_section_crisis_merged(df, service_users, supply, deficit_yrs, deficit_sets):
    if not deficit_yrs:
        st.info("Deficit-zone data not available.")
        return

    su_yrs = set(int(y) for y in service_users['year'].dropna().unique())
    sp_yrs = set(int(y) for y in supply['year'].dropna().unique())
    yrs_available = sorted(y for y in (su_yrs & sp_yrs) if y >= 2023)
    if not yrs_available:
        st.info("No overlapping years between service_users and supply.")
        return

    # ── KPI cards row: crisis count per year ────────────────────────────────
    st.markdown(
        '<div class="sub-h">Crisis zones over time — where home-care demand outpaces beds</div>',
        unsafe_allow_html=True,
    )

    cards_html = []
    for idx, yr in enumerate(deficit_yrs):
        count = len(deficit_sets[yr])
        if idx == 0:
            delta_block = ''
        else:
            prev_yr = deficit_yrs[idx - 1]
            new_z = deficit_sets[yr] - deficit_sets[prev_yr]
            resolved_z = deficit_sets[prev_yr] - deficit_sets[yr]
            net = len(new_z) - len(resolved_z)
            sign = '+' if net > 0 else ('' if net == 0 else '−')
            color = C['red'] if net > 0 else '#3D8B40' if net < 0 else '#6B7C93'
            delta_block = (
                f'<div style="color:{color};font-size:11px;margin-top:4px;font-weight:600">'
                f'{sign}{abs(net)} net vs {prev_yr}'
                f'</div>'
            )

        cards_html.append(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">{yr} Crisis Zones'
            f'<span class="kpi-help" data-tooltip="SA3s with waitlist pressure &gt; 1.0 in {yr}">?</span>'
            f'</div>'
            f'<div class="kpi-value">{count}</div>'
            f'{delta_block}'
            f'</div>'
        )

    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat({len(deficit_yrs)},1fr);'
        f'gap:16px;margin:0 0 14px">{"".join(cards_html)}</div>',
        unsafe_allow_html=True,
    )

    if len(deficit_yrs) >= 2:
        y_prev, y_curr = deficit_yrs[-2], deficit_yrs[-1]
        new_z = deficit_sets[y_curr] - deficit_sets[y_prev]
        resolved_z = deficit_sets[y_prev] - deficit_sets[y_curr]
        net_change = len(new_z) - len(resolved_z)
        st.warning(
            f"⚠️ **{y_prev}→{y_curr}:** **{len(new_z)} SA3s entered deficit**, "
            f"**{len(resolved_z)} resolved** → "
            f"**{'+' if net_change >= 0 else ''}{net_change} net** crisis "
            f"communities in a single year."
        )

    # ── Sub-section: Which SA3s? Bar + drill side-by-side ──────────────────
    st.markdown("---")
    st.markdown(
        '<div class="sub-h">Which SA3s? Click any bar to drill into HCP mix</div>',
        unsafe_allow_html=True,
    )

    # Controls — placed right before the bar+drill they control
    c_year, c_dir, c_n = st.columns([1.5, 1, 1])
    with c_year:
        year_sel = st.radio(
            "Year",
            options=yrs_available,
            index=len(yrs_available) - 1,
            horizontal=True,
            key="ch3_year",
        )
    with c_dir:
        direction = st.radio(
            "Direction",
            options=["Worst", "Best"],
            index=0,
            horizontal=True,
            key="ch3_direction",
        )
    with c_n:
        top_n = st.slider(
            "Top N",
            min_value=5, max_value=20, value=10, step=5,
            key="ch3_top_n",
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

    df_uniq = df_yr.drop_duplicates('sa3_name')
    df_uniq = df_uniq[df_uniq['waitlist_pressure'] > 0]
    if direction == "Worst":
        top_df = df_uniq.nlargest(top_n, 'waitlist_pressure').sort_values('waitlist_pressure').copy()
        bar_color_quartile = C['red']
        bar_color_other = C['navy']
        title_kind = 'Worst'
        sub_caption = 'Red = top quartile (highest pressure)'
    else:
        top_df = df_uniq.nsmallest(top_n, 'waitlist_pressure').sort_values('waitlist_pressure', ascending=False).copy()
        bar_color_quartile = C['teal']
        bar_color_other = C['navy']
        title_kind = 'Best'
        sub_caption = 'Teal = bottom quartile (lowest pressure)'

    if top_df.empty:
        st.info(f"No SA3s with positive waitlist pressure in {year_sel}.")
    else:
        if direction == "Worst":
            threshold = top_df['waitlist_pressure'].quantile(0.75)
            top_df['colour'] = top_df['waitlist_pressure'].apply(
                lambda x: bar_color_quartile if x >= threshold else bar_color_other
            )
        else:
            threshold = top_df['waitlist_pressure'].quantile(0.25)
            top_df['colour'] = top_df['waitlist_pressure'].apply(
                lambda x: bar_color_quartile if x <= threshold else bar_color_other
            )
        top_df['row_label'] = top_df['sa3_name'] + ' (' + top_df['state'] + ')'

        bar_col, drill_col = st.columns([1.4, 1])

        with bar_col:
            fig_wp = px.bar(
                top_df,
                x='waitlist_pressure', y='row_label', orientation='h',
                color='colour', color_discrete_map='identity',
                text='waitlist_pressure',
                custom_data=['sa3_code', 'sa3_name', 'state',
                             'hcp_level1', 'hcp_level2', 'hcp_level3', 'hcp_level4',
                             'hcp_high_needs', 'residential_places'],
                title=(f'{title_kind} {top_n} SA3 by Waitlist Pressure ({year_sel})<br>'
                       f'<sup>{sub_caption}</sup>'),
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
            fig_wp.add_vline(
                x=1.0, line_dash='dash', line_color=C['red'], line_width=1.5,
                annotation_text='Demand = Supply',
                annotation_position='top right',
            )
            fig_wp.update_layout(showlegend=False)
            theme(fig_wp, height=520)

            event = st.plotly_chart(
                fig_wp,
                use_container_width=True,
                on_select='rerun',
                selection_mode='points',
                key=f'ch3_wp_bar_{year_sel}_{direction}_{top_n}',
            )

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

        nat = (
            service_users[service_users['year'] == year_sel]
            .groupby('year')[HCP_COLS].sum().reset_index()
        )

        if selected_row is not None:
            row_for_donut = selected_row
            sub_label = selected_label
        else:
            if not nat.empty:
                nat_row = nat.iloc[0]
                row_for_donut = {c: int(nat_row[c]) for c in HCP_COLS}
            else:
                row_for_donut = {c: 0 for c in HCP_COLS}
            sub_label = 'National average · click a bar to drill into one SA3'

        with drill_col:
            donut_title = f'HCP mix — {sub_label} ({year_sel})'
            fig_drill = _hcp_donut(row_for_donut, title=donut_title, height=440)
            fig_drill.update_layout(
                showlegend=True,
                legend=dict(
                    orientation='v',
                    yanchor='middle', y=0.5,
                    xanchor='left', x=1.02,
                    font=dict(size=11),
                ),
                margin=dict(t=70, b=20, l=10, r=10),
            )
            st.plotly_chart(fig_drill, use_container_width=True)

            total = sum(row_for_donut[c] for c in HCP_COLS)
            st.metric('Total home-care users', f'{int(total):,d}')

    # ── Sub-section: Crisis Zones vs Rest of Australia line chart ───────────
    def_year = deficit_yrs[-1]
    crisis_codes = deficit_sets[def_year]
    if not crisis_codes:
        return

    st.markdown("---")
    st.markdown(
        '<div class="sub-h">Are beds flowing to where demand is?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#3D4F63;font-size:14px;margin:0 0 12px;line-height:1.6">'
        'Hold the crisis-zone set fixed at the latest waitlist-pressure snapshot, '
        'then trace residential-bed supply from 2019 onward for those SA3s vs '
        'everyone else.</p>',
        unsafe_allow_html=True,
    )

    sup_grp = supply.copy()
    sup_grp['group'] = sup_grp['sa3_code'].apply(
        lambda c: 'Crisis Zones' if c in crisis_codes else 'Rest of Australia'
    )
    sup_agg = (
        sup_grp.groupby(['group', 'year'], as_index=False)['residential_places'].sum()
    )

    base_year = int(sup_agg['year'].min())
    latest_year = int(sup_agg['year'].max())
    base = (
        sup_agg[sup_agg['year'] == base_year][['group', 'residential_places']]
        .rename(columns={'residential_places': '_base'})
    )
    sup_agg = sup_agg.merge(base, on='group', how='left')
    sup_agg['pct_change'] = (sup_agg['residential_places'] - sup_agg['_base']) / sup_agg['_base'] * 100

    fig_crisis = px.line(
        sup_agg.sort_values('year'),
        x='year', y='pct_change', color='group',
        color_discrete_map={'Crisis Zones': C['red'], 'Rest of Australia': C['teal']},
        markers=True,
        title=(f'Residential beds — % change from {base_year} ({base_year}→{latest_year})<br>'
               f'<sup>{len(crisis_codes)} crisis zones (waitlist > 1.0 in {def_year}) '
               f'vs the rest</sup>'),
        labels={'pct_change': f'% change from {base_year}', 'year': '', 'group': ''},
    )
    fig_crisis.add_hline(y=0, line_dash='dot', line_color=C['muted'], line_width=1)
    fig_crisis.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    theme(fig_crisis, height=380)
    st.plotly_chart(fig_crisis, use_container_width=True)

    def _row(group, year):
        sel = sup_agg[(sup_agg['group'] == group) & (sup_agg['year'] == year)]
        return int(sel['residential_places'].iloc[0]) if not sel.empty else 0

    crisis_base = _row('Crisis Zones', base_year)
    crisis_end = _row('Crisis Zones', latest_year)
    rest_base = _row('Rest of Australia', base_year)
    rest_end = _row('Rest of Australia', latest_year)
    crisis_delta = crisis_end - crisis_base
    rest_delta = rest_end - rest_base

    st.warning(
        f"💡 Between **{base_year} and {latest_year}**, the "
        f"**{len(crisis_codes)} crisis zones** "
        f"{'lost' if crisis_delta < 0 else 'added'} "
        f"**{abs(crisis_delta):,} beds** "
        f"({crisis_base:,} → {crisis_end:,}), while the rest of Australia "
        f"{'gained' if rest_delta > 0 else 'lost'} "
        f"**{abs(rest_delta):,} beds** "
        f"({rest_base:,} → {rest_end:,}). New supply is flowing toward "
        f"regions that already have enough — misallocation, not shortage."
    )


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
        f'<div style="display:inline-block;background:{C["red"]};color:white;'
        f'padding:5px 14px;border-radius:14px;font-size:11px;font-weight:700;'
        f'letter-spacing:0.08em;text-transform:uppercase;margin-bottom:10px">'
        f'The Reveal</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sec-h1">Which communities are being left behind?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sec-p">High-needs home-care demand is outpacing residential supply '
        'where the gap matters most — and new beds keep flowing toward regions that '
        'already have enough.</p>',
        unsafe_allow_html=True,
    )

    with st.expander("📖 Glossary — key terms in this chapter", expanded=False):
        st.markdown(
            f"""
<div style="color:{C['navy']};font-size:14px;line-height:1.7">
<ul style="margin:0;padding-left:22px">
  <li><b>Waitlist Pressure</b> = high-needs HCP users ÷ residential beds (per SA3).
      Values &gt; 1.0 mean home-care demand outpaces residential supply →
      <b>crisis zone</b> / <b>deficit zone</b>.</li>
  <li><b>HCP Levels</b> — Home Care Packages, L1 (Basic) → L4 (Very High needs).
      L4 should typically be in residential care, not home-based.</li>
  <li><b>Residential places</b> — aged-care facility beds, government-funded.</li>
  <li><b>SA3</b> — Statistical Area Level 3, ~331 regions in Australia (ABS).</li>
  <li><b>National HCP mix</b> — share of L1/L2/L3/L4 across all home-care users.</li>
</ul>
</div>
""",
            unsafe_allow_html=True,
        )

    if df.empty or service_users is None or service_users.empty:
        st.warning("No data for the current filter selection.")
        return

    # Compute deficit set per year — consumed by Tab Crisis zones
    deficit_yrs = sorted(
        y for y in (set(int(v) for v in service_users['year'].dropna().unique())
                    & set(int(v) for v in supply['year'].dropna().unique()))
        if y >= 2023
    )
    deficit_sets = {y: _deficit_set(service_users, supply, y) for y in deficit_yrs}

    # ── Three sub-tabs (Crisis zones + Worst SA3 merged) ────────────────────
    tab_nat, tab_crisis, tab_c = st.tabs([
        "🧭 National shift",
        "⚠️ Crisis zones",
        "👥 ACPR demographics",
    ])

    with tab_nat:
        _render_section_national(service_users)
    with tab_crisis:
        _render_section_crisis_merged(df, service_users, supply, deficit_yrs, deficit_sets)
    with tab_c:
        if acpr_res is not None and acpr_hc is not None:
            _render_section_c(acpr_res, acpr_hc)
        else:
            st.info("ACPR data not loaded.")
