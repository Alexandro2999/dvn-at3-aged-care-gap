import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from tabs.utils import C, ORG_COLOURS, MANDATE, theme


def render(ratings, master_filt, filter_active: bool = False) -> None:
    st.markdown(
        f'<div style="display:inline-block;background:{C["gold"]};color:white;'
        f'padding:5px 14px;border-radius:14px;font-size:17px;font-weight:700;'
        f'letter-spacing:0.08em;text-transform:uppercase;margin-bottom:10px">'
        f'The Verdict</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sec-h1">Did the Oct 2023 staffing mandate work?</div>',
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

    with st.expander("📖 Glossary — key terms in this chapter", expanded=False):
        st.markdown(
            f'<div style="color:{C["navy"]};font-size:20px;line-height:1.7">'
            f'<ul style="margin:0;padding-left:22px">'
            f'<li><b>Oct 2023 staffing mandate</b> — federal rule requiring 200 care minutes '
            f'per resident per day, 40 of which must come from a Registered Nurse.</li>'
            f'<li><b>RN minutes</b> — Registered Nurse minutes per resident per day '
            f'(mandate target: 44).</li>'
            f'<li><b>Care minutes (total)</b> — total direct care minutes per resident per day '
            f'(mandate target: 200).</li>'
            f'<li><b>Quality Measures</b> — one of 4 ACQSC star-rating sub-dimensions; '
            f'tracks clinical outcomes (pressure injuries, falls, weight loss, medications).</li>'
            f'<li><b>Fully compliant</b> — facility meeting <i>both</i> RN-minutes AND '
            f'total-care-minutes targets.</li>'
            f'<li><b>Before / After mandate</b> — snapshot date &lt; or ≥ 2023-10-01.</li>'
            f'</ul></div>',
            unsafe_allow_html=True,
        )

    # Recap pulls Ch2's national structural finding — compute from full ratings,
    # pre-filter, so it always shows the structural baseline regardless of sidebar.
    _means = _known_nat.groupby('org_type')['quality_score'].mean()
    if not _means.empty and 'government' in _means.index and 'profit' in _means.index:
        _govt = float(_means['government'])
        _profit = float(_means['profit'])
        _gap = _govt - _profit
        _n_snap = _known_nat['snapshot_date'].nunique()
        st.info(
            f"🔬 **Picking up from Chapter 2.** The structural ownership gap is "
            f"government **{_govt:.2f}★** vs for-profit **{_profit:.2f}★** — a "
            f"**{_gap:.2f}-point gap** stable across {_n_snap} quarterly snapshots. "
            f"This chapter tests whether the **October 2023 staffing mandate** "
            f"closed it. ← [Chapter 2: The Cause](?page=correlation) for "
            f"the diagnostic."
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
        st.info(
            f"📍 **Filter applied:** showing **{selected_states[0]}** only "
            f"({ratings['Service Name'].nunique():,} facilities)."
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

    # ── Three sub-tabs ───────────────────────────────────────────────────────
    tab_nat, tab_org, tab_wi = st.tabs([
        "🧭 Timeline",
        "👥 By owner",
        "🎚️ What-if",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB National trend
    # ════════════════════════════════════════════════════════════════════════
    with tab_nat:
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

        dims = ['residents_exp', 'staffing', 'compliance', 'quality_measures']
        dim_labels = ['Residents exp.', 'Staffing', 'Compliance', 'Quality measures']
        before_s = ratings[ratings['period'] == 'Before mandate'][dims].mean()
        after_s = ratings[ratings['period'] == 'After mandate'][dims].mean()
        sub_df = pd.DataFrame({
            'Sub-rating': dim_labels,
            'Before': before_s.values,
            'After': after_s.values,
        }).melt(id_vars='Sub-rating', var_name='Period', value_name='Score')
        fig_sub = px.bar(
            sub_df, x='Sub-rating', y='Score', color='Period',
            barmode='group',
            color_discrete_map={'Before': C['muted'], 'After': C['teal']},
            title='Sub-rating change before vs after mandate',
            labels={'Score': 'Avg score'},
        )
        theme(fig_sub, height=320)
        st.plotly_chart(fig_sub, use_container_width=True)

        if not (pd.isna(q_delta_f) or pd.isna(qm_delta_f)):
            st.info(
                f"⚖️ Quality rose **{q_delta_f:+.2f}** points after the mandate, but the "
                f"**Quality Measures** dimension barely moved (**{qm_delta_f:+.3f}**). "
                f"The mandate fixed inputs (staffing hours); it has not yet moved clinical outcomes."
            )

    # ════════════════════════════════════════════════════════════════════════
    # TAB By ownership
    # ════════════════════════════════════════════════════════════════════════
    with tab_org:
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

        org_time = (
            _known_f.groupby(['snapshot_date', 'org_type'])['quality_score']
            .mean().reset_index()
        )
        fig_org_t = px.line(
            org_time, x='snapshot_date', y='quality_score',
            color='org_type', color_discrete_map=ORG_COLOURS,
            title='Quality by ownership over time',
            labels={
                'quality_score': 'Avg quality score',
                'snapshot_date': 'Quarter',
                'org_type': 'Org type',
            },
        )
        fig_org_t.add_vline(
            x=MANDATE.timestamp() * 1000,
            line_dash='dash', line_color=C['red'],
            annotation_text='Oct 2023 mandate',
        )
        theme(fig_org_t, height=320)
        st.plotly_chart(fig_org_t, use_container_width=True)

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

        # ── State quality slope: pre vs post mandate ────────────────────────
        state_q = (
            _known_f.groupby(['state', 'period'])['quality_score'].mean().reset_index()
        )
        pivot = (
            state_q.pivot(index='state', columns='period', values='quality_score')
            .dropna(subset=['Before mandate', 'After mandate'])
        )
        if len(pivot) >= 2:
            pivot['delta'] = pivot['After mandate'] - pivot['Before mandate']
            st.markdown("---")
            st.markdown(
                '<div class="sub-h">Which state moved most? Quality pre vs post mandate</div>',
                unsafe_allow_html=True,
            )

            top_mover = pivot['delta'].idxmax()
            slope_fig = go.Figure()
            for state, row in pivot.iterrows():
                is_top = (state == top_mover)
                slope_fig.add_trace(go.Scatter(
                    x=['Pre-mandate', 'Post-mandate'],
                    y=[row['Before mandate'], row['After mandate']],
                    mode='lines+markers+text',
                    name=state,
                    line=dict(color=C['red'] if is_top else '#C8DCF0',
                              width=3 if is_top else 1.5),
                    marker=dict(size=12 if is_top else 8,
                                color=C['red'] if is_top else '#8FAFD0'),
                    text=[state, state],
                    textposition=['middle left', 'middle right'],
                    textfont=dict(size=15 if is_top else 10,
                                  color=C['red'] if is_top else C['muted']),
                    showlegend=False,
                    hovertemplate=f'<b>{state}</b><br>%{{x}}: %{{y:.2f}}★<extra></extra>',
                ))
            slope_fig.update_layout(
                title=f'State quality score — pre vs post Oct 2023 mandate<br>'
                      f'<sup>Largest mover highlighted in red</sup>',
                yaxis_title='Avg quality score',
                xaxis=dict(range=[-0.4, 1.4]),
            )
            theme(slope_fig, height=420)
            st.plotly_chart(slope_fig, use_container_width=True)

            mover_delta = float(pivot.loc[top_mover, 'delta'])
            rank_pre = pivot['Before mandate'].rank(ascending=False)
            rank_post = pivot['After mandate'].rank(ascending=False)
            top_rank_pre = int(rank_pre.loc[top_mover])
            top_rank_post = int(rank_post.loc[top_mover])
            st.success(
                f"💡 **{top_mover} rose {mover_delta:+.2f}★** — from rank "
                f"**{top_rank_pre}** ({pivot.loc[top_mover, 'Before mandate']:.2f}★ pre) "
                f"to rank **{top_rank_post}** "
                f"({pivot.loc[top_mover, 'After mandate']:.2f}★ post). "
                f"Proof case: ownership-level compliance moves outcomes."
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
