import streamlit as st
import pandas as pd
import plotly.express as px
from tabs.utils import C, ORG_COLOURS, MANDATE, theme


def render(ratings) -> None:
    st.markdown(
        '<div class="sec-h1">Did the Oct 2023 staffing mandate work?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sec-p"><b>Yes — but only for inputs, not outcomes.</b> '
        'National quality rose +0.25 pts (3.40 → 3.65, +7.3%) after Oct 2023. '
        'Staffing sub-rating jumped +0.51 pts — the largest gain. '
        'But quality measures (resident health outcomes) are flat at −0.015 pts. '
        'The mandate fixed staff hours; it has not yet fixed care.</p>',
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

    c1, c2 = st.columns(2)
    with c1:
        dims   = ['residents_exp', 'staffing', 'compliance', 'quality_measures']
        labels = ['Residents exp.', 'Staffing', 'Compliance', 'Quality measures']
        before = ratings[ratings['period'] == 'Before mandate'][dims].mean()
        after  = ratings[ratings['period'] == 'After mandate'][dims].mean()
        sub_df = pd.DataFrame({
            'Sub-rating': labels,
            'Before': before.values,
            'After':  after.values,
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

    with c2:
        org_time = (
            ratings[ratings['org_type'] != 'unknown']
            .groupby(['snapshot_date', 'org_type'])['quality_score']
            .mean().reset_index()
        )
        fig_org_t = px.line(
            org_time, x='snapshot_date', y='quality_score',
            color='org_type', color_discrete_map=ORG_COLOURS,
            title='Quality by org type over time',
            labels={
                'quality_score': 'Avg quality score',
                'snapshot_date': 'Quarter',
                'org_type': 'Org type',
            },
        )
        fig_org_t.add_vline(
            x=MANDATE.timestamp() * 1000,
            line_dash='dash', line_color=C['red'],
        )
        theme(fig_org_t, height=320)
        st.plotly_chart(fig_org_t, use_container_width=True)

    comp_time = (
        ratings[ratings['snapshot_date'] >= MANDATE]
        .dropna(subset=['fully_compliant'])
        .groupby('snapshot_date')['fully_compliant'].mean().reset_index()
    )
    comp_time['pct'] = comp_time['fully_compliant'] * 100
    fig_comp = px.line(
        comp_time, x='snapshot_date', y='pct',
        color_discrete_sequence=[C['navy']],
        title='% of facilities fully compliant with staffing minutes — post-mandate',
        labels={'pct': '% fully compliant', 'snapshot_date': 'Quarter'},
    )
    fig_comp.add_hline(
        y=65, line_dash='dot', line_color=C['teal'],
        annotation_text='65% target', annotation_position='top right',
    )
    theme(fig_comp, height=280)
    st.plotly_chart(fig_comp, use_container_width=True)

    # ── What-IF compliance threshold slider ─────────────────────────────────
    st.markdown("---")
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
        )
        fig_hist.add_vline(
            x=44, line_dash='dot', line_color=C['muted'],
            annotation_text='Mandate 44', annotation_position='top left',
        )
        theme(fig_hist, height=280)
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
