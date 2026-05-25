"""Chapter 3 — The Victims: who pays when access falls behind demand.

Advanced feature implemented here:
    Click-drill interactivity in the SA3 drilldown section.
    Clicking any bar in the waitlist-pressure chart fires Plotly's
    `on_select='rerun'` event; the selected SA3 then drives the HCP
    level-mix donut beside it. Enables a "click to investigate" pattern
    without a separate dropdown.
"""

import pandas as pd
# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import plotly.express as px
from tabs.utils import C, chapter_breadcrumb, chapter_closer, theme, data_caption

HCP_COLS = ['hcp_level1', 'hcp_level2', 'hcp_level3', 'hcp_level4']
LEVEL_LABELS = {
    'hcp_level1': 'L1 — Basic',
    'hcp_level2': 'L2 — Moderate',
    'hcp_level3': 'L3 — High',
    'hcp_level4': 'L4 — Very High',
}
LEVEL_ORDER = ['L1 — Basic', 'L2 — Moderate', 'L3 — High',
               'L4 — Very High']
LEVEL_COLOURS = {
    'L1 — Basic':       '#A6C8FF',   # light blue (low need)
    'L2 — Moderate':    '#3D6FA0',   # medium blue
    'L3 — High':        '#D9A53B',   # ochre (PPT gold, warning)
    'L4 — Very High':   '#B23A30',   # deep coral (alert — should be in residential)
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
    Honours whatever SA3 scope is in the input frames (filtered or full)."""
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
# Section: Crisis zones — national context → SA3 drilldown → bed flow
# ─────────────────────────────────────────────────────────────────────────────
def _render_section_crisis_merged(df, service_users, supply, deficit_yrs, deficit_sets, filter_active=False):
    if not deficit_yrs:
        st.info("Deficit-zone data not available.")
        return

    # Shared compute used by both sub-tabs
    nat = (
        service_users.groupby('year')[HCP_COLS]
        .sum().reset_index().sort_values('year')
    )
    nat_yrs = sorted(int(y) for y in nat['year'].unique())
    su_yrs = set(int(y) for y in service_users['year'].dropna().unique())
    sp_yrs = set(int(y) for y in supply['year'].dropna().unique())
    yrs_available = sorted(y for y in (su_yrs & sp_yrs) if y >= 2023)
    if not yrs_available:
        st.info("No overlapping years between service_users and supply.")
        return

    # ── Section 1: National demand context (L4 growth + crisis counts) ──────
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
            color = C['red'] if net > 0 else C['teal'] if net < 0 else C['muted']
            delta_block = (
                f'<div style="color:{color};font-size:17px;margin-top:4px;font-weight:600">'
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

    # ── Section 2: SA3 drilldown — Top-N bar + click-driven HCP donut ───────
    st.markdown("---")
    st.markdown(
        '<div class="sub-h">Which SA3s? Click any bar to drill into HCP mix</div>',
        unsafe_allow_html=True,
    )

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
        f'<div style="background:#FFF0F0;border-left:4px solid {C["red"]};'
        f'padding:10px 16px;border-radius:6px;margin:0 0 14px;'
        f'color:{C["navy"]};font-size:18px;line-height:1.5">'
        f'🚨 <b>{n_deficit_yr} crisis SA3s</b> in {year_sel} · '
        f'Worst: <b>{worst["sa3_name"]} ({worst["state"]})</b> '
        f'<b style="color:{C["red"]}">{worst["waitlist_pressure"]:.2f}×</b> — '
        f'{int(worst["hcp_high_needs"]):,} high-needs people / '
        f'{int(worst["residential_places"]):,} beds'
        f'</div>',
        unsafe_allow_html=True,
    )

    df_uniq = df_yr.drop_duplicates('sa3_name')
    df_uniq = df_uniq[df_uniq['waitlist_pressure'] > 0]
    if direction == "Worst":
        top_df = df_uniq.nlargest(top_n, 'waitlist_pressure').sort_values('waitlist_pressure').copy()
        bar_color_quartile = C['red']
        bar_color_other = C['navy']
        title_kind = 'Worst'
        sub_caption = '⚠ Red = top quartile (highest pressure) · bars past 1.0× line are in crisis'
    else:
        top_df = df_uniq.nsmallest(top_n, 'waitlist_pressure').sort_values('waitlist_pressure', ascending=False).copy()
        bar_color_quartile = C['teal']
        bar_color_other = C['navy']
        title_kind = 'Best'
        sub_caption = '✓ Teal = bottom quartile (lowest pressure)'

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
        # Icon prefix so the crisis threshold (1.0) is readable without colour —
        # supports colourblind users and screen-zoom + greyscale printing.
        top_df['bar_text'] = top_df['waitlist_pressure'].apply(
            lambda v: f"⚠ {v:.3f}" if v >= 1.0 else f"✓ {v:.3f}"
        )

        bar_col, drill_col = st.columns([1.4, 1])

        with bar_col:
            fig_wp = px.bar(
                top_df,
                x='waitlist_pressure', y='row_label', orientation='h',
                color='colour', color_discrete_map='identity',
                text='bar_text',
                custom_data=['sa3_code', 'sa3_name', 'state',
                             'hcp_level1', 'hcp_level2', 'hcp_level3', 'hcp_level4',
                             'hcp_high_needs', 'residential_places'],
                title=(f'{title_kind} {top_n} SA3 by Waitlist Pressure ({year_sel})<br>'
                       f'<sup>{sub_caption}</sup>'),
                labels={'waitlist_pressure': 'Waitlist Pressure Index', 'row_label': ''},
            )
            fig_wp.update_traces(
                texttemplate='%{text}', textposition='outside',
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
            st.markdown(data_caption("AIHW GEN Home Care + Residential, SA3 × year · click a bar to drill into HCP levels"), unsafe_allow_html=True)

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

        nat_yr = (
            service_users[service_users['year'] == year_sel]
            .groupby('year')[HCP_COLS].sum().reset_index()
        )

        if selected_row is not None:
            row_for_donut = selected_row
            sub_label = selected_label
        else:
            if not nat_yr.empty:
                nat_row = nat_yr.iloc[0]
                row_for_donut = {c: int(nat_row[c]) for c in HCP_COLS}
            else:
                row_for_donut = {c: 0 for c in HCP_COLS}
            sub_label = (
                'Aggregate for current filter · click a bar to drill into one SA3'
                if filter_active else
                'National average · click a bar to drill into one SA3'
            )

        with drill_col:
            donut_title = f'HCP mix — {sub_label} ({year_sel})'
            fig_drill = _hcp_donut(row_for_donut, title=donut_title, height=380)
            fig_drill.update_layout(
                showlegend=True,
                legend=dict(
                    orientation='h',
                    yanchor='top', y=-0.05,
                    xanchor='center', x=0.5,
                    font=dict(size=14),
                    entrywidth=0.5,
                    entrywidthmode='fraction',
                ),
                margin=dict(t=70, b=100, l=10, r=10),
            )
            st.plotly_chart(fig_drill, use_container_width=True)
            st.markdown(data_caption("AIHW GEN Home Care Package data, latest year · L1=basic → L4=very high need"), unsafe_allow_html=True)

            total = sum(row_for_donut[c] for c in HCP_COLS)
            st.metric('Total home-care users', f'{int(total):,d}')

    # ── Section 3: Crisis Zones vs Rest of Australia line chart ─────────────
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
        '<p style="color:#4A5A6E;font-size:20px;margin:0 0 12px;line-height:1.6">'
        'Hold the crisis-zone set fixed at the latest waitlist-pressure snapshot, '
        'then trace residential-bed supply across the 2023–2025 window for those '
        'SA3s vs everyone else.</p>',
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
    _crisis_yrs = sorted(int(y) for y in sup_agg['year'].unique())
    fig_crisis.update_xaxes(
        tickmode='array', tickvals=_crisis_yrs,
        ticktext=[str(y) for y in _crisis_yrs],
    )
    theme(fig_crisis, height=380)
    st.plotly_chart(fig_crisis, use_container_width=True)
    st.markdown(data_caption("AIHW GEN residential places by SA3, 2023–2025 · crisis = waitlist pressure > 1.0"), unsafe_allow_html=True)

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
        + ("\n\n*Scope: SA3s currently in the State + Remoteness filter.*" if filter_active else "")
    )

    # ── Chapter closer: takeaways + next chapter CTA ──────────────────────────
    _latest_def_n = len(deficit_sets[deficit_yrs[-1]])
    st.markdown(
        chapter_closer(3, [
            f"<b>{_latest_def_n} SA3 regions</b> have demand exceeding supply "
            f"(waitlist pressure &gt; 1.0) in {deficit_yrs[-1]} — these are crisis zones.",
            "The <b>L4 (very-high needs) cohort</b> is growing fastest — system is "
            "becoming heavier-needs, not lighter.",
            f"Crisis zones <b>lost {abs(crisis_delta):,} beds</b> while the rest of Australia "
            f"{'gained' if rest_delta > 0 else 'lost'} {abs(rest_delta):,} — beds are "
            f"flowing the <b>wrong direction</b>.",
        ]),
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────
def render(df, supply, n_deficit: int, service_users=None, filter_active: bool = False) -> None:
    st.markdown(chapter_breadcrumb(3), unsafe_allow_html=True)
    st.markdown(
        f'<div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin:0 0 8px">'
        f'<span style="background:{C["red"]};color:white;padding:3px 10px;'
        f'border-radius:10px;font-size:13px;font-weight:700;letter-spacing:0.06em;'
        f'text-transform:uppercase">The Victims</span>'
        f'<span class="sec-h1" style="margin:0">Which communities are being left behind?</span>'
        f'</div>',
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
<div style="color:{C['navy']};font-size:20px;line-height:1.7">
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
        st.warning(
            "**No SA3s match your current sidebar filter.** "
            "Try expanding State or Remoteness in the left panel — "
            "or clear the filter to see the national picture."
        )
        return

    # Apply global filter via SA3 membership from master_filt — only when the
    # sidebar is actively narrowed. At default scope we keep the full national
    # service_users + supply universe so the hero crisis-zone count matches the
    # nationally-reported figure (otherwise SA3s without quality data drop out).
    if filter_active:
        _allowed_sa3 = set(df['sa3_code'].dropna().unique())
        if _allowed_sa3:
            service_users = service_users[service_users['sa3_code'].isin(_allowed_sa3)].copy()
            supply = supply[supply['sa3_code'].isin(_allowed_sa3)].copy()

    if service_users.empty or supply.empty:
        st.warning(
            "**No SA3s match your current sidebar filter** (State + Remoteness). "
            "Try expanding the selection in the left panel — or clear the filter "
            "to see the national picture."
        )
        return

    # Compute deficit set per year — now scoped to the active filter
    deficit_yrs = sorted(
        y for y in (set(int(v) for v in service_users['year'].dropna().unique())
                    & set(int(v) for v in supply['year'].dropna().unique()))
        if y >= 2023
    )
    deficit_sets = {y: _deficit_set(service_users, supply, y) for y in deficit_yrs}

    _render_section_crisis_merged(df, service_users, supply, deficit_yrs, deficit_sets, filter_active=filter_active)
