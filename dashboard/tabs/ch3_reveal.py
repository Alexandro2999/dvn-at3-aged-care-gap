import streamlit as st
import plotly.express as px
from tabs.utils import C, theme


def render(df, year_sel: int, n_deficit: int) -> None:
    st.markdown('<div class="sec-h1">Which communities are being left behind?</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("No data for the current filter selection.")
        return

    worst_rows = df.drop_duplicates('sa3_name').nlargest(1, 'waitlist_pressure')
    if not worst_rows.empty:
        worst = worst_rows.iloc[0]
        st.markdown(
            f'<p class="sec-p">In <b>{year_sel}</b>, <b>{n_deficit} SA3 regions</b> have more '
            f'high-needs home care users than available residential beds. The worst is '
            f'<b>{worst["sa3_name"]} ({worst["state"]})</b> with a pressure ratio of '
            f'<b>{worst["waitlist_pressure"]:.2f}</b> — '
            f'{int(worst["hcp_high_needs"]):,} people competing for '
            f'{int(worst["residential_places"]):,} beds.</p>',
            unsafe_allow_html=True,
        )

    top20 = (
        df.nlargest(30, 'waitlist_pressure')
        .drop_duplicates('sa3_name').head(20)
        .sort_values('waitlist_pressure').copy()
    )
    q75 = top20['waitlist_pressure'].quantile(0.75)
    top20['colour'] = top20['waitlist_pressure'].apply(lambda x: C['red'] if x >= q75 else C['navy'])
    top20['row_label'] = top20['sa3_name'] + ' (' + top20['state'] + ')'

    fig_wp = px.bar(
        top20,
        x='waitlist_pressure', y='row_label', orientation='h',
        color='colour', color_discrete_map='identity',
        text='waitlist_pressure',
        hover_data={
            'state': True, 'hcp_high_needs': ':,d',
            'residential_places': ':,d', 'waitlist_pressure': ':.3f',
        },
        title=f'Top 20 SA3 Regions by Waitlist Pressure ({year_sel})<br>'
              '<sup>Red = top quartile (highest pressure)</sup>',
        labels={'waitlist_pressure': 'Waitlist Pressure Index', 'row_label': ''},
    )
    fig_wp.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    fig_wp.add_vline(x=1.0, line_dash='dash', line_color=C['red'], line_width=1.5,
                     annotation_text='Demand = Supply', annotation_position='top right')
    fig_wp.update_layout(showlegend=False)
    theme(fig_wp, height=520)
    st.plotly_chart(fig_wp, use_container_width=True)

    st.markdown('<div class="sub-h">Who is actually waiting?</div>', unsafe_allow_html=True)
    hcp_melt = top20.melt(
        id_vars=['sa3_name', 'waitlist_pressure'],
        value_vars=['hcp_level1', 'hcp_level2', 'hcp_level3', 'hcp_level4'],
        var_name='level', value_name='users',
    )
    hcp_melt['level_label'] = hcp_melt['level'].map({
        'hcp_level1': 'L1 — Basic',
        'hcp_level2': 'L2 — Moderate',
        'hcp_level3': 'L3 — High (near-residential)',
        'hcp_level4': 'L4 — Very High (should be residential)',
    })
    level_order = [
        'L1 — Basic', 'L2 — Moderate',
        'L3 — High (near-residential)',
        'L4 — Very High (should be residential)',
    ]
    fig_hcp = px.bar(
        hcp_melt,
        x='sa3_name', y='users', color='level_label',
        category_orders={'sa3_name': top20['sa3_name'].tolist(), 'level_label': level_order},
        color_discrete_map={
            'L1 — Basic':                           '#A6C8FF',
            'L2 — Moderate':                        '#4589FF',
            'L3 — High (near-residential)':         C['gold'],
            'L4 — Very High (should be residential)': C['red'],
        },
        barmode='stack',
        title=f'HCP Level Composition by SA3: Who Is Actually Waiting? ({year_sel})',
        labels={'users': 'Home care users', 'sa3_name': '', 'level_label': 'Care level'},
    )
    fig_hcp.update_layout(
        xaxis_tickangle=45,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    )
    theme(fig_hcp, height=400)
    st.plotly_chart(fig_hcp, use_container_width=True)

    # ADVANCED FEATURE 3 — What-If scenario
    st.markdown(
        '<div class="whatif-box">'
        '<div class="whatif-title">What-IF Scenario</div>'
        '<p class="whatif-sub">If all SA3s reached this beds_per_1k target, '
        'how many exit the red zone?</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    whatif_target = st.slider(
        "Target beds per 1,000 elderly",
        min_value=30.0, max_value=80.0, value=50.0, step=1.0,
        label_visibility="collapsed",
    )
    n_below = int((df['beds_per_1k'] < whatif_target).sum())
    n_above = int(len(df) - n_below)
    nat_avg_beds = (
        float(df['residential_places'].sum() / df['pop_65_plus'].sum() * 1000)
        if df['pop_65_plus'].sum() > 0 else 0.0
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("SA3s below target", f"{n_below}", help=f"Below {whatif_target:.0f} beds/1k elderly")
    m2.metric("SA3s at or above target", f"{n_above}")
    m3.metric("National avg beds/1k", f"{nat_avg_beds:.1f}")

    med_beds = df['beds_per_1k'].median()
    fig_wi = px.histogram(
        df, x='beds_per_1k', nbins=30,
        color_discrete_sequence=[C['teal']],
        title=f'Distribution of beds per 1,000 elderly — target at {whatif_target:.0f}',
        labels={'beds_per_1k': 'Beds per 1,000 Elderly (65+)'},
    )
    fig_wi.add_vline(x=whatif_target, line_dash='dash', line_color=C['red'],
                     annotation_text=f'Target: {whatif_target:.0f} beds/1k',
                     annotation_position='top right')
    fig_wi.add_vline(x=med_beds, line_dash='dot', line_color=C['muted'],
                     annotation_text=f'Median: {med_beds:.1f}',
                     annotation_position='top left')
    theme(fig_wi, height=300)
    st.plotly_chart(fig_wi, use_container_width=True)
