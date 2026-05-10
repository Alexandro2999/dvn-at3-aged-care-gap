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
