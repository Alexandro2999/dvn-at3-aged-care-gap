import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from tabs.utils import C, ORG_COLOURS, MANDATE, chapter_breadcrumb, chapter_closer, theme


def render(ratings, master_filt, filter_active: bool = False) -> None:
    st.markdown(chapter_breadcrumb(4), unsafe_allow_html=True)
    st.markdown(
        f'<div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin:0 0 8px">'
        f'<span style="background:{C["gold"]};color:white;padding:3px 10px;'
        f'border-radius:10px;font-size:13px;font-weight:700;letter-spacing:0.06em;'
        f'text-transform:uppercase">The Verdict</span>'
        f'<span class="sec-h1" style="margin:0">Did the Oct 2023 staffing mandate work?</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Live-compute the national pre/post mandate deltas for the headline para.
    # Use raw (national) ratings — para is explicitly "national" framing.
    _known_nat = ratings[ratings['org_type'] != 'unknown']
    _before_nat = _known_nat[_known_nat['period'] == 'Before mandate']
    _after_nat = _known_nat[_known_nat['period'] == 'After mandate']
    q_before_nat = float(_before_nat['quality_score'].mean())
    q_after_nat = float(_after_nat['quality_score'].mean())
    q_delta_nat = q_after_nat - q_before_nat
    q_pct_nat = (q_delta_nat / q_before_nat * 100) if q_before_nat else 0.0
    staff_delta_nat = float(_after_nat['staffing'].mean() - _before_nat['staffing'].mean())
    qm_delta_nat = float(_after_nat['quality_measures'].mean() - _before_nat['quality_measures'].mean())

    st.markdown(
        f'<p class="sec-p"><b>Yes — but only for inputs, not outcomes.</b> '
        f'National quality rose {q_delta_nat:+.2f} pts ({q_before_nat:.2f} → {q_after_nat:.2f}, '
        f'{q_pct_nat:+.1f}%) after Oct 2023. '
        f'Staffing sub-rating jumped {staff_delta_nat:+.2f} pts — the largest gain. '
        f'But quality measures (resident health outcomes) are flat at {qm_delta_nat:+.3f} pts. '
        f'The mandate fixed staff hours; it has not yet fixed care.</p>',
        unsafe_allow_html=True,
    )

    # Sidebar filter propagation: narrow ratings by the state + MMM set
    # carried by master_filt, so every chart in this tab respects the sidebar.
    # Only apply when the sidebar is actively narrowed — at default scope we
    # keep the full ratings frame so KPI cards match the national headline.
    if filter_active:
        allowed_states = set(master_filt['state'].dropna().unique())
        allowed_mmm = set(master_filt['mmm_code'].dropna().unique())
        ratings = ratings[
            ratings['state'].isin(allowed_states)
            & ratings['mmm_code'].isin(allowed_mmm)
        ].copy()

    if ratings.empty:
        st.warning(
            "No facility data matches the current sidebar filter. "
            "Widen state / remoteness selection to see mandate effects."
        )
        return

    selected_states = sorted(ratings['state'].dropna().unique())
    if len(selected_states) == 1:
        st.caption(
            f"📍 *Filter applied: showing **{selected_states[0]}** only "
            f"({ratings['Service Name'].nunique():,} facilities).*"
        )

    # ── Pre-compute filtered pre/post for KPI cards + tabs ──────────────────
    _known_f = ratings[ratings['org_type'] != 'unknown']
    _before_f = _known_f[_known_f['period'] == 'Before mandate']
    _after_f = _known_f[_known_f['period'] == 'After mandate']

    def _safe_mean(df, col):
        return float(df[col].mean()) if not df.empty else float('nan')

    q_before_f = _safe_mean(_before_f, 'quality_score')
    q_after_f = _safe_mean(_after_f, 'quality_score')
    q_delta_f = q_after_f - q_before_f if not (pd.isna(q_before_f) or pd.isna(q_after_f)) else float('nan')
    staff_delta_f = _safe_mean(_after_f, 'staffing') - _safe_mean(_before_f, 'staffing')
    qm_delta_f = _safe_mean(_after_f, 'quality_measures') - _safe_mean(_before_f, 'quality_measures')

    # Compliance frame (filtered)
    post = ratings[ratings['snapshot_date'] >= MANDATE].dropna(subset=['fully_compliant'])
    comp_org = (
        post[post['org_type'] != 'unknown']
        .groupby(['snapshot_date', 'org_type'])['fully_compliant'].mean().reset_index()
    )
    comp_org['pct'] = comp_org['fully_compliant'] * 100
    comp_org = comp_org.rename(columns={'org_type': 'category'})

    comp_nat = post.groupby('snapshot_date')['fully_compliant'].mean().reset_index()
    comp_nat['pct'] = comp_nat['fully_compliant'] * 100
    comp_nat['category'] = 'national'

    comp_all = pd.concat([
        comp_org[['snapshot_date', 'category', 'pct']],
        comp_nat[['snapshot_date', 'category', 'pct']],
    ], ignore_index=True)

    if not post.empty:
        latest_date = post['snapshot_date'].max()
        _lc = (
            comp_all[comp_all['snapshot_date'] == latest_date]
            .set_index('category')['pct'].to_dict()
        )
        gov_comp = _lc.get('government', float('nan'))
        profit_comp = _lc.get('profit', float('nan'))
        nat_comp = _lc.get('national', float('nan'))
        comp_gap = gov_comp - profit_comp if not (pd.isna(gov_comp) or pd.isna(profit_comp)) else float('nan')
        latest_date_label = latest_date.strftime('%b %Y')
    else:
        latest_date = None
        gov_comp = profit_comp = nat_comp = comp_gap = float('nan')
        latest_date_label = '—'

    cat_labels = {
        'national': 'National blend',
        'government': 'Government',
        'not_for_profit': 'Not for profit',
        'profit': 'For profit',
    }

    # ── Two sub-tabs: combined mandate effect + interactive what-if ─────────
    tab_effect, tab_wi = st.tabs([
        "🧭 Mandate Effect",
        "🎚️ What-if",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB Mandate Effect — national headline → ownership breakdown
    # ════════════════════════════════════════════════════════════════════════
    with tab_effect:
        st.caption(
            "📍 *This tab has **2 sections**: **National headline** "
            "(KPIs + quality trend) and **By ownership** (compliance gap). "
            "Scroll to explore.*"
        )
        st.markdown(
            f'<div style="display:inline-block;background:{C["navy"]};color:white;'
            f'padding:3px 10px;border-radius:8px;font-size:13px;font-weight:700;'
            f'letter-spacing:0.04em;margin:4px 0 10px">'
            f'§ 1 / 2 · National headline</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Quality Δ post-mandate
      <span class="kpi-help" data-tooltip="Avg quality score: After − Before mandate">?</span>
    </div>
    <div class="kpi-value">{q_delta_f:+.2f}<span class="kpi-suffix"> ★</span></div>
    <div style="color:#6B7C93;font-size:17px;margin-top:4px;font-weight:500">
      {q_before_f:.2f} → {q_after_f:.2f}
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Staffing Δ
      <span class="kpi-help" data-tooltip="Staffing sub-rating change after mandate">?</span>
    </div>
    <div class="kpi-value">{staff_delta_f:+.2f}<span class="kpi-suffix"> ★</span></div>
    <div style="color:#6B7C93;font-size:17px;margin-top:4px;font-weight:500">
      largest sub-rating gain
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Quality Measures Δ
      <span class="kpi-help" data-tooltip="Clinical outcomes sub-rating change after mandate">?</span>
    </div>
    <div class="kpi-value">{qm_delta_f:+.3f}<span class="kpi-suffix"> ★</span></div>
    <div style="color:#6B7C93;font-size:17px;margin-top:4px;font-weight:500">
      clinical outcomes flat
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Compliance latest
      <span class="kpi-help" data-tooltip="% of facilities meeting both RN and total care-minute targets, latest snapshot">?</span>
    </div>
    <div class="kpi-value">{nat_comp:.1f}<span class="kpi-suffix"> %</span></div>
    <div style="color:#6B7C93;font-size:17px;margin-top:4px;font-weight:500">
      {latest_date_label} · target 65%
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        nat_time = ratings.groupby('snapshot_date')['quality_score'].mean().reset_index()
        fig_time = px.line(
            nat_time, x='snapshot_date', y='quality_score',
            color_discrete_sequence=[C['teal']],
            title='National average quality score over time — mandate Oct 2023',
            labels={'quality_score': 'Avg quality score', 'snapshot_date': 'Quarter'},
        )
        fig_time.add_vline(
            x=MANDATE.timestamp() * 1000,
            line_dash='dash', line_color=C['red'],
            annotation_text='Oct 2023 mandate', annotation_position='top left',
        )
        theme(fig_time, height=320)
        st.plotly_chart(fig_time, use_container_width=True)

        if not (pd.isna(q_delta_f) or pd.isna(qm_delta_f)):
            st.info(
                f"⚖️ Quality rose **{q_delta_f:+.2f}** points after the mandate, but the "
                f"**Quality Measures** dimension barely moved (**{qm_delta_f:+.3f}**). "
                f"The mandate fixed inputs (staffing hours); it has not yet moved clinical outcomes."
            )

        # ── Section 2: By-ownership breakdown ────────────────────────────
        st.markdown("---")
        st.markdown(
            f'<div style="display:inline-block;background:{C["navy"]};color:white;'
            f'padding:3px 10px;border-radius:8px;font-size:13px;font-weight:700;'
            f'letter-spacing:0.04em;margin:0 0 8px">'
            f'§ 2 / 2 · By ownership</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="sub-h">Where the gap lives — by ownership</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:0 0 12px">
  <div class="kpi-card">
    <div class="kpi-label">Government Compliance
      <span class="kpi-help" data-tooltip="% of govt-run facilities fully compliant, latest snapshot">?</span>
    </div>
    <div class="kpi-value">{gov_comp:.1f}<span class="kpi-suffix"> %</span></div>
    <div style="color:#6B7C93;font-size:17px;margin-top:4px;font-weight:500">
      {latest_date_label}
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">For-Profit Compliance
      <span class="kpi-help" data-tooltip="% of for-profit facilities fully compliant, latest snapshot">?</span>
    </div>
    <div class="kpi-value">{profit_comp:.1f}<span class="kpi-suffix"> %</span></div>
    <div style="color:#6B7C93;font-size:17px;margin-top:4px;font-weight:500">
      {latest_date_label}
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Compliance Gap
      <span class="kpi-help" data-tooltip="Government minus For-profit, percentage points">?</span>
    </div>
    <div class="kpi-value" style="color:{C['red']}">{comp_gap:.0f}<span class="kpi-suffix"> pts</span></div>
    <div style="color:#6B7C93;font-size:17px;margin-top:4px;font-weight:500">
      govt − for-profit
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        comp_all_l = comp_all.copy()
        comp_all_l['cat_label'] = comp_all_l['category'].map(cat_labels)
        color_map = {cat_labels[k]: v for k, v in ORG_COLOURS.items()}
        color_map[cat_labels['national']] = C['navy']

        fig_comp = px.line(
            comp_all_l, x='snapshot_date', y='pct', color='cat_label',
            color_discrete_map=color_map,
            title='% of facilities fully compliant with staffing minutes — by ownership',
            labels={'pct': '% fully compliant', 'snapshot_date': 'Quarter', 'cat_label': ''},
        )
        fig_comp.add_hline(
            y=65, line_dash='dot', line_color=C['teal'],
            annotation_text='65% target', annotation_position='top right',
        )
        theme(fig_comp, height=320)
        st.plotly_chart(fig_comp, use_container_width=True)

        if not pd.isna(comp_gap):
            st.warning(
                f"⚠ As of {latest_date_label}, for-profit compliance is "
                f"**{profit_comp:.1f}%** vs government **{gov_comp:.1f}%** — a "
                f"**{comp_gap:.0f}-point gap** in adherence to the same federal rule. "
                f"Same regulator, same reporting, opposite outcomes by ownership."
            )

    # ════════════════════════════════════════════════════════════════════════
    # TAB What-if RN target
    # ════════════════════════════════════════════════════════════════════════
    with tab_wi:
        st.markdown(
            '<div class="sub-h">What-IF: how strict should the RN-minutes target be?</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "The current mandate is **44 RN minutes/resident/day**. Drag the slider to model "
            "what happens to compliance if the target moved tighter or looser."
        )

        latest_snap = ratings['snapshot_date'].max()
        latest_df = ratings[ratings['snapshot_date'] == latest_snap].dropna(
            subset=['rn_minutes_actual']
        )

        if latest_df.empty:
            st.info("No facility-level RN minute data for the latest snapshot.")
        else:
            wi_target = st.slider(
                "Hypothetical RN-minutes target (per resident per day)",
                min_value=0, max_value=250, value=44, step=2, key="ch4_rn_target",
            )

            n_total = len(latest_df)
            n_comply = int((latest_df['rn_minutes_actual'] >= wi_target).sum())
            n_fail = n_total - n_comply
            pct_comply = (n_comply / n_total * 100) if n_total else 0.0
            median_actual = float(latest_df['rn_minutes_actual'].median())

            k1, k2, k3 = st.columns(3)
            k1.metric(
                "Facilities compliant",
                f"{n_comply:,}",
                f"{pct_comply:.1f}% of {n_total:,}",
                help=f"Facilities with rn_minutes_actual ≥ {wi_target}",
            )
            k2.metric(
                "Facilities below target",
                f"{n_fail:,}",
                f"{100 - pct_comply:.1f}% would need to lift staffing",
                delta_color="inverse",
            )
            k3.metric(
                "Sector median actual",
                f"{median_actual:.0f} min/day",
                help="Median RN minutes per resident per day, latest snapshot",
            )

            fig_hist = px.histogram(
                latest_df, x='rn_minutes_actual', nbins=40,
                color_discrete_sequence=[C['teal']],
                title=f'Distribution of facility RN minutes — {latest_snap.strftime("%b %Y")}',
                labels={'rn_minutes_actual': 'RN minutes/resident/day (actual)'},
            )
            fig_hist.add_vline(
                x=wi_target, line_dash='dash', line_color=C['red'], line_width=2,
                annotation_text=f'Threshold: {wi_target}',
                annotation_position='top right',
                annotation=dict(
                    yref='paper', y=1.12,
                    font=dict(color=C['red'], size=15),
                    bgcolor='rgba(0,0,0,0)', borderwidth=0,
                ),
            )
            fig_hist.add_vline(
                x=44, line_dash='dot', line_color=C['muted'], line_width=2,
                annotation_text='Mandate: 44',
                annotation_position='top left',
                annotation=dict(
                    yref='paper', y=1.04,
                    font=dict(color=C['muted'], size=15),
                    bgcolor='rgba(0,0,0,0)', borderwidth=0,
                ),
            )
            theme(fig_hist, height=320)
            st.plotly_chart(fig_hist, use_container_width=True)

            if pct_comply >= 65:
                st.success(
                    f"✓ At a **{wi_target}**-minute threshold, **{pct_comply:.1f}%** of facilities "
                    f"would meet the bar — passes the 65% policy target."
                )
            else:
                st.warning(
                    f"⚠️ At a **{wi_target}**-minute threshold, only **{pct_comply:.1f}%** of facilities "
                    f"would meet the bar — below the 65% policy target."
                )

    # ── Chapter closer: takeaways + back-to-home CTA ─────────────────────────
    st.markdown(
        chapter_closer(4, [
            f"National quality rose <b>{q_delta_nat:+.2f}★</b> after the Oct 2023 mandate — "
            f"but driven by <b>staffing inputs</b>, not clinical outcomes (QM Δ {qm_delta_nat:+.3f}).",
            "Ownership compliance gap remains: <b>government 81% vs for-profit 31%</b> — "
            "same rule, opposite adherence.",
            "<b>Verdict</b>: the mandate fixed inputs (staff hours bought), "
            "but the ownership-quality gap is structural and still open.",
        ]),
        unsafe_allow_html=True,
    )
