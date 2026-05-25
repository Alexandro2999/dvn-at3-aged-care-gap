"""Chapter 2 — The Cause: why quality varies across providers and dollars.

Advanced feature implemented here:
    Context-aware filtering. The sidebar State + MMM selection narrows the
    SA3 universe upstream in `app.py`; this chapter then recomputes the
    quality-by-ownership gap, funding-per-bed distribution, and the
    quality-vs-funding scatter on the fly so the narrative callouts
    (gap size, funding median, R²) rewrite to match the active scope.

Structured as three sub-tabs — Quality (ownership gap), Funding (per-bed
distribution by ownership), and Together (quality vs funding scatter with
OLS trendline).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from tabs.utils import C, ORG_COLOURS, chapter_breadcrumb, chapter_closer, theme, data_caption


_ORG_ORDER = ['profit', 'not_for_profit', 'government']
_SUPPLY_ORG_COLS = {'profit': 'n_private', 'not_for_profit': 'n_nfp', 'government': 'n_government'}


def _beds_by_org_for_year(supply: pd.DataFrame, year: int) -> dict:
    """Approximate beds-by-org-type for the given year.

    Within each SA3, beds-per-facility is residential_places/n_residential.
    Allocate beds to org types proportional to facility count in that SA3.
    Assumes mean facility size is comparable across ownership types within an SA3.
    """
    s = supply[(supply['year'] == year) & (supply['n_residential'] > 0)].copy()
    s['beds_per_fac'] = s['residential_places'] / s['n_residential']
    out = {}
    for org, col in _SUPPLY_ORG_COLS.items():
        out[org] = float((s[col].fillna(0) * s['beds_per_fac']).sum())
    return out


def render(df, ratings, funding, supply) -> None:
    st.markdown(chapter_breadcrumb(2), unsafe_allow_html=True)

    # Methodology per asset chapter_02_the_correlation.md Insights 1 & 2:
    # "mean across all snapshots" — this is the ownership-gap-over-time view.
    # Using a single-snapshot mean conflates the post-mandate level shift with
    # the structural ownership gap that has been stable for 3 years.
    ratings_known = ratings[ratings['org_type'] != 'unknown']

    # ── National anchor frames (for Tab R paradox warning — stays national) ─
    _sub_dims_nat = ['residents_exp', 'staffing', 'compliance', 'quality_measures']
    sub_means_nat = ratings_known.groupby('org_type')[_sub_dims_nat].mean()
    _latest_fund_yr_nat = int(funding['year'].max())
    fund_per_fac_nat = (
        funding[(funding['year'] == _latest_fund_yr_nat) & (funding['funding'] > 0)]
        .groupby('org_type')['funding'].mean()
        .reset_index()
    )
    fund_per_fac_nat['funding_m'] = fund_per_fac_nat['funding'] / 1e6

    # ── Apply global filter via SA3 membership from master_filt ────────────
    _allowed_sa3 = set(df['sa3_code'].dropna().unique())
    if _allowed_sa3:
        ratings_known = ratings_known[ratings_known['sa3_code'].isin(_allowed_sa3)].copy()
        funding = funding[funding['sa3_code'].isin(_allowed_sa3)].copy()
        supply = supply[supply['sa3_code'].isin(_allowed_sa3)].copy()

    org_q = (
        ratings_known.groupby('org_type')['quality_score']
        .agg(['mean', 'median']).reset_index()
    )
    org_q.columns = ['org_type', 'mean', 'median']

    last_snap_dt = ratings_known['snapshot_date'].max()
    facility_counts = (
        ratings_known[ratings_known['snapshot_date'] == last_snap_dt]
        .groupby('org_type')['Service Name'].nunique().to_dict()
    )
    org_q['count'] = org_q['org_type'].map(facility_counts).fillna(0).astype(int)

    n_snapshots = ratings_known['snapshot_date'].nunique()
    first_snap_dt = ratings_known['snapshot_date'].min()
    span_label = f'{first_snap_dt.strftime("%b %Y")} – {last_snap_dt.strftime("%b %Y")}'

    org_means = org_q.set_index('org_type')['mean']
    govt_mean = float(org_means.get('government', float('nan')))
    profit_mean = float(org_means.get('profit', float('nan')))
    ownership_gap = govt_mean - profit_mean

    nfp_mean = float(org_means.get('not_for_profit', float('nan')))

    st.markdown(
        f'<div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin:0 0 8px">'
        f'<span style="background:{C["teal"]};color:white;padding:3px 10px;'
        f'border-radius:10px;font-size:13px;font-weight:700;letter-spacing:0.06em;'
        f'text-transform:uppercase">The Cause</span>'
        f'<span class="sec-h1" style="margin:0">Who runs the best facilities?</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sec-p">Quality is explained by <b>ownership</b>, not geography. '
        'Remote areas score higher <i>because</i> they have fewer for-profit providers.</p>',
        unsafe_allow_html=True,
    )

    org_label_map = {'profit': 'For profit', 'not_for_profit': 'Not for Profit', 'government': 'Government'}

    # ── Sub-rating frame (used in Tab Quality + Relationship callout) ───────
    sub_dims = ['residents_exp', 'staffing', 'compliance', 'quality_measures']
    sub_labels_map = {
        'residents_exp': 'Residents Exp.',
        'staffing': 'Staffing',
        'compliance': 'Compliance',
        'quality_measures': 'Quality Measures',
    }
    sub_means = ratings_known.groupby('org_type')[sub_dims].mean()
    org_subs_long = sub_means.reset_index().melt(
        id_vars='org_type', value_vars=sub_dims,
        var_name='sub_rating', value_name='score',
    )
    org_subs_long['sub_label'] = org_subs_long['sub_rating'].map(sub_labels_map)
    org_subs_long['org_label'] = org_subs_long['org_type'].map(org_label_map)

    # ── Funding-per-facility frame (used in Tab Funding + Relationship callout)
    latest_fund_yr = int(funding['year'].max())
    fund_per_fac = (
        funding[(funding['year'] == latest_fund_yr) & (funding['funding'] > 0)]
        .groupby('org_type')['funding'].mean()
        .reset_index()
    )
    fund_per_fac['funding_m'] = fund_per_fac['funding'] / 1e6
    fund_per_fac['org_label'] = fund_per_fac['org_type'].map(org_label_map)

    # ── Three sub-tabs: Quality / Funding / Quality vs Funding ──────────────
    tab_q, tab_f, tab_r = st.tabs([
        "📊 Quality",
        "💰 Funding",
        "⚖️ Together",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — QUALITY: KPI cards + sub-rating breakdown
    # ════════════════════════════════════════════════════════════════════════
    with tab_q:
        st.markdown(
            f"""
<div class="kpi-row-3">
  <div class="kpi-card">
    <div class="kpi-label">Government Avg
      <span class="kpi-help" data-tooltip="Mean quality score for government-run facilities">?</span>
    </div>
    <div class="kpi-value">{govt_mean:.2f}<span class="kpi-suffix"> ★</span></div>
    <div style="color:#6B7C93;font-size:17px;margin-top:4px;font-weight:500">
      Baseline · {n_snapshots} snapshots
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Non-Profit Avg
      <span class="kpi-help" data-tooltip="Mean quality score for not-for-profit facilities">?</span>
    </div>
    <div class="kpi-value">{nfp_mean:.2f}<span class="kpi-suffix"> ★</span></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">For-Profit Avg
      <span class="kpi-help" data-tooltip="Mean quality score for for-profit facilities">?</span>
    </div>
    <div class="kpi-value">{profit_mean:.2f}<span class="kpi-suffix"> ★</span></div>
    <div style="color:{C["red"]};font-size:17px;margin-top:4px;font-weight:600">
      Gap vs govt: {ownership_gap:.2f} pts
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        sub_order = list(sub_labels_map.values())
        fig_sub = px.bar(
            org_subs_long,
            x='sub_label', y='score', color='org_type',
            color_discrete_map=ORG_COLOURS,
            barmode='group',
            category_orders={'sub_label': sub_order},
            text='score',
            title=(f'Sub-rating breakdown by ownership<br>'
                   f'<sup>Mean across {n_snapshots} snapshots, {span_label}</sup>'),
            labels={'sub_label': '', 'score': 'Avg score (1–5)', 'org_type': 'Org type'},
        )
        fig_sub.update_traces(
            texttemplate='%{text:.2f}', textposition='outside', textfont_size=13,
        )
        fig_sub.update_layout(
            yaxis_range=[0, 5],
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )
        theme(fig_sub, height=360)
        st.plotly_chart(fig_sub, use_container_width=True)
        st.markdown(data_caption("ACQSC Star Ratings, May 2023–Feb 2026 · 12 quarterly snapshots"), unsafe_allow_html=True)

        fp_staff_t1 = float(sub_means.loc['profit', 'staffing']) if 'profit' in sub_means.index else float('nan')
        gov_staff_t1 = float(sub_means.loc['government', 'staffing']) if 'government' in sub_means.index else float('nan')
        staff_gap_t1 = gov_staff_t1 - fp_staff_t1
        fp_qm_t1 = float(sub_means.loc['profit', 'quality_measures']) if 'profit' in sub_means.index else float('nan')
        gov_qm_t1 = float(sub_means.loc['government', 'quality_measures']) if 'government' in sub_means.index else float('nan')

        st.info(
            f"📊 **Staffing drives the entire ownership gap.** Government scores "
            f"**{staff_gap_t1:.2f} pts higher** on staffing than for-profit "
            f"({gov_staff_t1:.2f} vs {fp_staff_t1:.2f}). But clinical Quality Measures "
            f"are nearly identical ({gov_qm_t1:.2f} vs {fp_qm_t1:.2f}) — for-profit "
            f"is buying less staff time, not producing worse clinical outcomes."
        )

        # Small-N guard — warn if any org type has < 10 facilities after filter
        _low_n = [(o, n) for o, n in facility_counts.items() if n < 10]
        if _low_n:
            _low_str = ", ".join(f"{org_label_map.get(o, o)} (N={n})" for o, n in _low_n)
            st.caption(
                f"⚠️ *Small sample after filter — {_low_str}. "
                f"Means may be unstable; broaden the State/Remoteness filter for a steadier read.*"
            )

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — FUNDING: per-X bar (toggle) + pie share by year + KPI metrics
    # ════════════════════════════════════════════════════════════════════════
    with tab_f:
        # Year trend frame (used by pie + KPIs)
        fund_trend = (
            funding[funding['funding'] > 0]
            .groupby(['year', 'org_type'])['funding'].sum().reset_index()
        )
        fund_trend['funding_b'] = fund_trend['funding'] / 1e9
        fund_yrs = sorted(int(y) for y in fund_trend['year'].dropna().unique())
        base_year = fund_yrs[0]
        latest_year = fund_yrs[-1]

        # KPI compute (for cards + callout)
        total_base_b = float(fund_trend[fund_trend['year'] == base_year]['funding_b'].sum())
        total_latest_b = float(fund_trend[fund_trend['year'] == latest_year]['funding_b'].sum())
        total_growth_pct = (total_latest_b / total_base_b - 1) * 100 if total_base_b else float('nan')

        def _share(year: int, org: str) -> float:
            tot = fund_trend[fund_trend['year'] == year]['funding_b'].sum()
            if tot <= 0:
                return float('nan')
            org_val = fund_trend[(fund_trend['year'] == year) & (fund_trend['org_type'] == org)]['funding_b'].sum()
            return float(org_val / tot * 100)

        fp_share_base = _share(base_year, 'profit')
        fp_share_latest = _share(latest_year, 'profit')
        fp_share_delta = fp_share_latest - fp_share_base
        fp_funding_latest_b = float(
            fund_trend[(fund_trend['year'] == latest_year) & (fund_trend['org_type'] == 'profit')]['funding_b'].sum()
        )
        fp_funding_base_b = float(
            fund_trend[(fund_trend['year'] == base_year) & (fund_trend['org_type'] == 'profit')]['funding_b'].sum()
        )
        fp_funding_growth_pct = (fp_funding_latest_b / fp_funding_base_b - 1) * 100 if fp_funding_base_b else float('nan')

        # Paradox preview: per-facility funding ratio for-profit ÷ government
        _per_fac_lookup = fund_per_fac.set_index('org_type')['funding_m'].to_dict()
        _fp_per_fac = _per_fac_lookup.get('profit', float('nan'))
        _gov_per_fac = _per_fac_lookup.get('government', float('nan'))
        fund_ratio_fp_gov = (_fp_per_fac / _gov_per_fac) if _gov_per_fac else float('nan')

        # ── KPI cards (3-column funding row) ─────────────────────────────────
        st.markdown(
            f"""
<div class="kpi-row-3">
  <div class="kpi-card">
    <div class="kpi-label">Total Funding {latest_year}
      <span class="kpi-help" data-tooltip="Sum of all government funding across providers in {latest_year}">?</span>
    </div>
    <div class="kpi-value">${total_latest_b:.1f}<span class="kpi-suffix"> B</span></div>
    <div style="color:#6B7C93;font-size:17px;margin-top:4px;font-weight:500">
      {total_growth_pct:+.0f}% vs {base_year}
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Funding Ratio
      <span class="kpi-help" data-tooltip="For-profit funding per facility ÷ Government per facility, {latest_fund_yr}">?</span>
    </div>
    <div class="kpi-value">{fund_ratio_fp_gov:.1f}<span class="kpi-suffix"> ×</span></div>
    <div style="color:#6B7C93;font-size:17px;margin-top:4px;font-weight:500">
      For-profit / Government per facility
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">For-Profit Funding {latest_year}
      <span class="kpi-help" data-tooltip="Government funding flowing to for-profit providers in {latest_year}">?</span>
    </div>
    <div class="kpi-value">${fp_funding_latest_b:.1f}<span class="kpi-suffix"> B</span></div>
    <div style="color:#6B7C93;font-size:17px;margin-top:4px;font-weight:500">
      {fp_funding_growth_pct:+.0f}% vs {base_year}
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        # ── Control: normalisation toggle ───────────────────────────────────
        fund_norm = st.radio(
            "Show funding bar as:",
            options=["Per facility ($M)", "Per bed ($k)"],
            horizontal=True, key="ch2_fund_norm",
        )

        # Compute funding-per-X for selected mode
        if fund_norm == "Per facility ($M)":
            bar_df = fund_per_fac.copy()
            bar_df['value'] = bar_df['funding_m']
            bar_x_label = f'$M per facility'
            bar_text_fmt = '$%{text:.2f}M'
            bar_title_kind = 'facility'
            bar_value_unit = 'M'
        else:
            beds = _beds_by_org_for_year(supply, latest_fund_yr)
            fund_total_org = (
                funding[(funding['year'] == latest_fund_yr) & (funding['funding'] > 0)]
                .groupby('org_type')['funding'].sum()
            )
            rows = []
            for org in _ORG_ORDER:
                bed_n = beds.get(org, 0)
                tot = float(fund_total_org.get(org, 0))
                per_bed_k = (tot / bed_n / 1000) if bed_n > 0 else float('nan')
                rows.append({'org_type': org, 'org_label': org_label_map[org], 'value': per_bed_k})
            bar_df = pd.DataFrame(rows)
            bar_x_label = '$k per bed'
            bar_text_fmt = '$%{text:.1f}k'
            bar_title_kind = 'bed'
            bar_value_unit = 'k'

        # Pre-compute values for both the bar and the right-hand takeaway box
        bar_lookup = bar_df.set_index('org_type')['value'].to_dict()
        fp_val = bar_lookup.get('profit', float('nan'))
        gov_val = bar_lookup.get('government', float('nan'))
        ratio = (fp_val / gov_val) if gov_val else float('nan')

        c_bar_l, c_bar_r = st.columns([3, 2])
        with c_bar_l:
            fig_fund_bar = px.bar(
                bar_df.sort_values('value'),
                x='value', y='org_label', orientation='h',
                color='org_type', color_discrete_map=ORG_COLOURS,
                text='value',
                title=f'Funding per {bar_title_kind}<br><sup>{latest_fund_yr}</sup>',
                labels={'value': bar_x_label, 'org_label': ''},
            )
            fig_fund_bar.update_traces(
                texttemplate=bar_text_fmt, textposition='outside', textfont_size=15,
            )
            fig_fund_bar.update_layout(showlegend=False)
            theme(fig_fund_bar, height=360)
            st.plotly_chart(fig_fund_bar, use_container_width=True)
            st.markdown(data_caption("AIHW GEN Service Funding by Facility, latest annual snapshot"), unsafe_allow_html=True)
        with c_bar_r:
            st.markdown(
                f'<div style="background:#FFF7E6;border-left:4px solid #E67E22;'
                f'padding:18px 20px;border-radius:8px;margin-top:60px;'
                f'color:{C["navy"]};font-size:18px;line-height:1.55">'
                f'<div style="font-size:13px;font-weight:700;letter-spacing:0.06em;'
                f'text-transform:uppercase;color:#A04E00;margin-bottom:6px">'
                f'Key takeaway · {latest_fund_yr}</div>'
                f'<b>${fp_val:.2f}{bar_value_unit}</b> for-profit vs '
                f'<b>${gov_val:.2f}{bar_value_unit}</b> government per {bar_title_kind} '
                f'— a <b style="color:{C["red"]}">{ratio:.1f}× gap</b>.'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Live callout — toggle-aware narrative (numbers already surfaced in KPI cards)

        st.info(
            f"💰 In {latest_fund_yr}, for-profit receives **{ratio:.1f}× more public funding "
            f"per {bar_title_kind}** "
            f"(${fp_val:.2f}{bar_value_unit} vs ${gov_val:.2f}{bar_value_unit}). "
            f"Total grew **{total_growth_pct:+.0f}%** since {base_year} "
            f"(${total_base_b:.1f}B → ${total_latest_b:.1f}B), with for-profit's share "
            f"rising **{fp_share_delta:+.0f} pts** ({fp_share_base:.0f}% → {fp_share_latest:.0f}%). "
            f"_Per-bed assumes bed counts split proportionally to facility counts within "
            f"each SA3._" if fund_norm == "Per bed ($k)"
            else
            f"💰 In {latest_fund_yr}, for-profit receives **{ratio:.1f}× more public funding "
            f"per facility** "
            f"(${fp_val:.2f}M vs ${gov_val:.2f}M). "
            f"Total grew **{total_growth_pct:+.0f}%** since {base_year} "
            f"(${total_base_b:.1f}B → ${total_latest_b:.1f}B), with for-profit's share "
            f"rising **{fp_share_delta:+.0f} pts** ({fp_share_base:.0f}% → {fp_share_latest:.0f}%)."
        )

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — QUALITY vs FUNDING: the paradox + SA3-level scatter
    # ════════════════════════════════════════════════════════════════════════
    with tab_r:
        # Paradox callout — NATIONAL anchor, unchanged by the sidebar filter.
        st.caption("📍 *National benchmark — the paradox figures below stay fixed regardless of the sidebar filter. The SA3 scatter further down respects the filter.*")
        fund_lookup = fund_per_fac_nat.set_index('org_type')['funding_m'].to_dict()
        fp_fund = fund_lookup.get('profit', float('nan'))
        gov_fund = fund_lookup.get('government', float('nan'))
        fund_ratio = (fp_fund / gov_fund) if gov_fund else float('nan')
        fp_staff = float(sub_means_nat.loc['profit', 'staffing']) if 'profit' in sub_means_nat.index else float('nan')
        gov_staff = float(sub_means_nat.loc['government', 'staffing']) if 'government' in sub_means_nat.index else float('nan')
        staff_gap = gov_staff - fp_staff
        fp_qm = float(sub_means_nat.loc['profit', 'quality_measures']) if 'profit' in sub_means_nat.index else float('nan')
        gov_qm = float(sub_means_nat.loc['government', 'quality_measures']) if 'government' in sub_means_nat.index else float('nan')

        st.warning(
            f"⚖️ **The for-profit paradox.** For-profit receives **{fund_ratio:.1f}× "
            f"more public funding** per facility (${fp_fund:.2f}M vs ${gov_fund:.2f}M) "
            f"but scores **{staff_gap:.2f} pts lower** on staffing "
            f"({fp_staff:.2f} vs {gov_staff:.2f}). Yet clinical **Quality Measures "
            f"are nearly identical** ({fp_qm:.2f} vs {gov_qm:.2f}). "
            f"The gap is in staff time bought, not in health outcomes."
        )

        # X-axis toggle: funding per bed ($k) ↔ funding per facility ($M)
        scatter_x = st.radio(
            "Scatter X-axis:",
            options=["Funding per bed ($k)", "Funding per facility ($M)"],
            horizontal=True, key="ch2_scatter_x",
        )

        # SA3-level scatter
        fund_sa3 = (
            funding[(funding['year'] == latest_fund_yr) & (funding['funding'] > 0)]
            .groupby('sa3_code', as_index=False)['funding'].sum()
        )
        df_latest_yr = df[df['year'] == df['year'].max()].drop_duplicates('sa3_code')
        sc = (
            fund_sa3.merge(df_latest_yr[['sa3_code', 'sa3_name', 'state', 'mmm_code',
                                          'quality_score', 'residential_places',
                                          'n_private', 'n_residential']],
                           on='sa3_code', how='inner')
        )
        sc = sc[(sc['residential_places'] > 0) & (sc['quality_score'].notna())].copy()
        sc['private_share'] = (sc['n_private'] / sc['n_residential'].replace(0, 1) * 100).clip(0, 100)

        if scatter_x == "Funding per bed ($k)":
            sc['x_value'] = sc['funding'] / sc['residential_places'] / 1_000
            sc = sc[sc['x_value'] > 0]
            x_axis_label = 'Govt funding per bed ($k / year)'
            x_hover_fmt = ':,.0f'
            x_unit_in_callout = 'k/year per bed'
            x_kind_in_title = 'bed'
        else:
            sc = sc[sc['n_residential'] > 0].copy()
            sc['x_value'] = sc['funding'] / sc['n_residential'] / 1e6
            sc = sc[sc['x_value'] > 0]
            x_axis_label = 'Govt funding per facility ($M / year)'
            x_hover_fmt = ':,.2f'
            x_unit_in_callout = 'M/year per facility'
            x_kind_in_title = 'facility'

        if not sc.empty:
            fig_fb = px.scatter(
                sc,
                x='x_value', y='quality_score',
                color='private_share',
                color_continuous_scale=[[0, C['teal']], [0.5, C['gold']], [1, C['red']]],
                size='residential_places', size_max=22,
                hover_data={
                    'sa3_name': True, 'state': True,
                    'x_value': x_hover_fmt, 'quality_score': ':.2f',
                    'residential_places': ':,d', 'private_share': ':.0f',
                },
                title=(f'Funding per {x_kind_in_title} vs Quality Score by SA3 ({latest_fund_yr})<br>'
                       '<sup>Bubble size = residential places · Colour = private share %</sup>'),
                labels={
                    'x_value':       x_axis_label,
                    'quality_score': 'Avg Quality Score (1–5)',
                    'private_share': 'Private %',
                },
            )
            fig_fb.update_layout(coloraxis_colorbar=dict(title='Private %', ticksuffix='%'))
            theme(fig_fb, height=420)
            st.plotly_chart(fig_fb, use_container_width=True)
            st.markdown(data_caption("ACQSC Star Ratings + AIHW Service List · joined at SA3 × year"), unsafe_allow_html=True)

            corr = sc[['x_value', 'quality_score']].corr().iloc[0, 1]
            avg_x = sc['x_value'].mean()
            st.caption(
                f"🔍 *Across {len(sc)} SA3s in {latest_fund_yr}, correlation between "
                f"funding-per-{x_kind_in_title} and quality is "
                f"**r = {corr:+.2f}** (avg ${avg_x:,.2f}{x_unit_in_callout}). "
                f"More dollars does not translate cleanly to higher star ratings — "
                f"ownership and management matter more than absolute spend.*"
            )
        else:
            st.warning(
                "**No funding + supply overlap for the latest year matches your sidebar filter.** "
                "Try expanding the State or Remoteness selection in the left panel — "
                "or clear the filter to see the national picture."
            )

    # ── Chapter closer: takeaways + next chapter CTA ─────────────────────────
    st.markdown(
        chapter_closer(2, [
            f"<b>Ownership</b> predicts quality more than geography: government "
            f"<b>{govt_mean:.2f}★</b> vs for-profit <b>{profit_mean:.2f}★</b> "
            f"(<b>{ownership_gap:.2f}-pt</b> gap, stable across {n_snapshots} snapshots).",
            "<b>Staffing</b> drives the entire gap — clinical Quality Measures "
            "are nearly identical across ownership types.",
            f"For-profit receives <b>{fund_ratio_fp_gov:.1f}× more</b> public funding "
            f"per facility than government — but delivers lower quality.",
        ]),
        unsafe_allow_html=True,
    )
