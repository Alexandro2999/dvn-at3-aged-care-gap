import streamlit as st
import plotly.express as px
from tabs.utils import C, ORG_COLOURS, MMM_COLOURS, theme


def render(df, ratings, funding, year_sel: int) -> None:
    st.markdown('<div class="sec-h1">Who runs the best facilities?</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sec-p">Quality differences are not explained by geography — they are explained '
        'by <b>ownership</b>. Government facilities average 4.21 vs for-profit 3.68 (gap = 0.53 pts). '
        'Remote areas score higher <i>because</i> they have fewer for-profit providers.</p>',
        unsafe_allow_html=True,
    )

    latest = ratings[ratings['snapshot_date'] == ratings['snapshot_date'].max()]
    latest = latest[latest['org_type'] != 'unknown']

    org_q = latest.groupby('org_type')['quality_score'].agg(['mean', 'median', 'count']).reset_index()
    org_q.columns = ['org_type', 'mean', 'median', 'count']
    nat_avg = latest['quality_score'].mean()
    org_label_map = {'profit': 'For profit', 'not_for_profit': 'Not for Profit', 'government': 'Government'}
    org_q['label'] = org_q['org_type'].map(org_label_map)
    org_q['annotation'] = org_q.apply(
        lambda r: f"{r['mean']:.2f}  (median {r['median']:.2f}, n={int(r['count']):,})", axis=1
    )

    fig_org = px.bar(
        org_q.sort_values('mean'),
        x='mean', y='label', orientation='h',
        color='org_type',
        color_discrete_map={k: ORG_COLOURS.get(k, C['teal']) for k in org_q['org_type']},
        text='annotation',
        title='Average Quality Score by Ownership Type<br><sup>February 2026 snapshot</sup>',
        labels={'mean': 'Avg Quality Score (1–5)', 'label': ''},
    )
    fig_org.add_vline(
        x=nat_avg, line_dash='dot', line_color=C['teal'],
        annotation_text=f'National avg {nat_avg:.2f}', annotation_position='top right',
    )
    fig_org.update_traces(textposition='outside', textfont_size=11)
    fig_org.update_layout(showlegend=False, xaxis_range=[0, 5])
    theme(fig_org, height=260)
    st.plotly_chart(fig_org, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_box = px.box(
            latest[latest['mmm_code'].notna()],
            x='mmm_code', y='quality_score', color='mmm_code',
            color_discrete_map=MMM_COLOURS,
            title='Quality Score by Remoteness (MMM)<br><sup>February 2026 snapshot</sup>',
            labels={'quality_score': 'Quality Score (1–5)', 'mmm_code': 'Remoteness'},
            category_orders={'mmm_code': ['MM1', 'MM2', 'MM3', 'MM4', 'MM5', 'MM6', 'MM7']},
        )
        nat_med = latest['quality_score'].median()
        fig_box.add_hline(
            y=nat_med, line_dash='dot', line_color=C['teal'],
            annotation_text=f'National median {nat_med:.2f}', annotation_position='top right',
        )
        fig_box.update_layout(showlegend=False)
        theme(fig_box, height=360)
        st.plotly_chart(fig_box, use_container_width=True)

    with c2:
        fund_trend = (
            funding[funding['funding'] > 0]
            .groupby(['year', 'org_type'])['funding'].sum().reset_index()
        )
        fund_trend['funding_b'] = fund_trend['funding'] / 1e9
        fig_fund = px.bar(
            fund_trend, x='year', y='funding_b', color='org_type',
            color_discrete_map=ORG_COLOURS, barmode='stack',
            title='Govt Funding by Ownership Type<br><sup>$B, 2019–2025</sup>',
            labels={'funding_b': 'Funding ($B)', 'org_type': 'Org type'},
        )
        fig_fund.update_layout(
            xaxis=dict(tickmode='linear', tick0=2019, dtick=1),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )
        theme(fig_fund, height=360)
        st.plotly_chart(fig_fund, use_container_width=True)
