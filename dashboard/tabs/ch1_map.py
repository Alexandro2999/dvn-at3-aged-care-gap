import pandas as pd
import streamlit as st
import plotly.express as px
from tabs.utils import C, MMM_COLOURS, theme

_METRIC_OPTIONS = {
    'Care Gap Index':      ('care_gap_index',    [[0, '#E3F1FA'], [0.4, '#4A7FC1'], [1, '#1B3F6E']], 'Care Gap Index'),
    'Quality Score':       ('quality_score',     [[0, '#FFF5E6'], [0.5, '#F5A623'], [1, '#8B4500']], 'Quality Score ★'),
    'Access Rate (%)':     ('access_rate',       [[0, '#F0FFF0'], [0.5, '#4CAF50'], [1, '#1B5E20']], 'Access Rate %'),
    'Waitlist Pressure':   ('waitlist_pressure', [[0, '#FFF0F0'], [0.5, '#E57373'], [1, '#7F0000']], 'Waitlist Pressure'),
}

MMM_ORDER = ['MM1', 'MM2', 'MM3', 'MM4', 'MM5', 'MM6', 'MM7']
MMM_LABELS = {
    'MM1': 'Major City', 'MM2': 'Inner Regional', 'MM3': 'Outer Regional',
    'MM4': 'Remote', 'MM5': 'Very Remote', 'MM6': 'Remote (alt)', 'MM7': 'Very Remote (alt)',
}


def render(df, gdf, year_sel: int) -> None:
    st.markdown('<div class="sec-h1">Is aged care near me any good?</div>', unsafe_allow_html=True)

    # --- Neighbourhood search (ADVANCED FEATURE 2 — fuzzy match with tooltip card) ---
    search = st.text_input("Check my neighbourhood", placeholder="Type your area name (SA3)")
    if search and not df.empty:
        try:
            from rapidfuzz import process as fz
            names = df['sa3_name'].dropna().unique().tolist()
            result = fz.extractOne(search, names)
            if result and result[1] >= 60:
                row = df[df['sa3_name'] == result[0]].iloc[0]
                st.markdown(
                    f'<div class="nb-card">'
                    f'<b>{result[0]}</b> ({row.get("state", "")})'
                    f'&nbsp;&nbsp;·&nbsp;&nbsp;Care Gap Index: <b>{row["care_gap_index"]:.2f}</b>'
                    f'&nbsp;&nbsp;·&nbsp;&nbsp;Quality Score: <b>{row["quality_score"]:.2f}★</b>'
                    f'&nbsp;&nbsp;·&nbsp;&nbsp;Access Rate: <b>{row["access_rate"]:.1f}%</b>'
                    f'&nbsp;&nbsp;·&nbsp;&nbsp;Remoteness: <b>{row.get("mmm_code", "")}</b>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        except Exception:
            pass

    # --- KPI metric cards ---
    if not df.empty:
        avg_cgi = df['care_gap_index'].mean()
        avg_qs  = df['quality_score'].mean()
        avg_ar  = df['access_rate'].mean()
        n_sa3   = len(df)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Avg Care Gap Index", f"{avg_cgi:.2f}", help="Mean care gap index across selected SA3s. Higher = more underserved.")
        k2.metric("SA3s Analysed", f"{n_sa3:,}", help="Number of SA3 regions in current filter selection.")
        k3.metric("Avg Quality Score", f"{avg_qs:.2f} ★", help="Mean facility quality score (out of 5) across selected SA3s.")
        k4.metric("Avg Access Rate", f"{avg_ar:.1f}%", help="Mean share of 65+ population in residential care across selected SA3s.")

    st.markdown(
        '<p class="sec-p">Each SA3 is coloured by the selected metric. '
        'Use the dropdown to switch between <b>Care Gap Index</b>, Quality, Access, or Waitlist Pressure. '
        'The care gap paradox: the deepest crisis is in major cities, not remote areas.</p>',
        unsafe_allow_html=True,
    )

    # --- Choropleth with metric selector ---
    metric_label = st.selectbox(
        "Map metric",
        options=list(_METRIC_OPTIONS.keys()),
        index=0,
        help="Choose which metric to display on the choropleth map.",
    )
    col_name, cscale, cbar_label = _METRIC_OPTIONS[metric_label]

    if gdf is not None and not df.empty:
        cols_needed = ['sa3_code', 'sa3_name', 'state', 'mmm_code',
                       'care_gap_index', 'quality_score', 'access_rate', 'waitlist_pressure', 'pop_65_plus']
        merged = gdf.merge(df[cols_needed], on='sa3_code', how='left')

        val_max = float(df[col_name].quantile(0.95)) if df[col_name].notna().any() else 5
        fig_map = px.choropleth(
            merged,
            geojson=merged.__geo_interface__,
            locations=merged.index,
            color=col_name,
            color_continuous_scale=cscale,
            range_color=[0, val_max if val_max > 0 else 5],
            hover_data={
                'sa3_name': True, 'state': True, 'mmm_code': True,
                'care_gap_index': ':.2f', 'quality_score': ':.2f',
                'access_rate': ':.1f', 'pop_65_plus': ':,.0f',
            },
            title=f'{metric_label} by SA3 ({year_sel})',
            labels={col_name: cbar_label},
        )
        fig_map.update_geos(fitbounds='locations', visible=False)
        fig_map.update_coloraxes(colorbar_title_text=cbar_label)
        theme(fig_map, height=520)
        st.plotly_chart(fig_map, use_container_width=True)
        st.warning(
            f"The 10 worst-performing SA3s by Care Gap Index are all in major cities (MM1). "
            f"Unley (SA) has a care gap index of **2.78** — more than 2× the national average of ~1.13."
        )
    elif not df.empty:
        st.warning("Shapefile not found — showing fallback scatter chart.")
        fig_fb = px.scatter(
            df.dropna(subset=['access_rate', 'quality_score']),
            x='access_rate', y='quality_score',
            color='care_gap_index', size='pop_65_plus',
            hover_name='sa3_name',
            hover_data={'state': True, 'mmm_code': True, 'care_gap_index': ':.2f'},
            color_continuous_scale=[[0, C['bg']], [1, C['navy']]],
            title=f'Access rate vs quality score ({year_sel})',
            labels={'access_rate': 'Access rate (%)', 'quality_score': 'Quality score'},
        )
        theme(fig_fb, height=480)
        st.plotly_chart(fig_fb, use_container_width=True)
    else:
        st.info("No data matches the current filter selection.")

    if not df.empty:
        # --- Worst CGI-10 (left) | Best access-10 (right) ---
        c1, c2 = st.columns(2)
        with c1:
            worst10 = df.nlargest(10, 'care_gap_index')[['sa3_name', 'state', 'care_gap_index']].copy()
            worst10['label'] = worst10['sa3_name'] + ' (' + worst10['state'] + ')'
            fig_worst = px.bar(
                worst10.sort_values('care_gap_index'),
                x='care_gap_index', y='label', orientation='h',
                color_discrete_sequence=[C['red']], text='care_gap_index',
                title=f'10 Worst Care Gap SA3s<br><sup>highest care gap index, {year_sel}</sup>',
                labels={'care_gap_index': 'Care Gap Index', 'label': ''},
            )
            fig_worst.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            theme(fig_worst, height=380)
            st.plotly_chart(fig_worst, use_container_width=True)
        with c2:
            top10 = df.nlargest(10, 'access_rate')[['sa3_name', 'state', 'access_rate']].copy()
            top10['label'] = top10['sa3_name'] + ' (' + top10['state'] + ')'
            fig_top = px.bar(
                top10.sort_values('access_rate'),
                x='access_rate', y='label', orientation='h',
                color_discrete_sequence=[C['teal']], text='access_rate',
                title=f'10 Best Served SA3s<br><sup>highest access rate, {year_sel}</sup>',
                labels={'access_rate': 'Access Rate (% of 65+ in residential care)', 'label': ''},
            )
            fig_top.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            theme(fig_top, height=380)
            st.plotly_chart(fig_top, use_container_width=True)

        # --- MMM quality bar chart (counterintuitive finding) ---
        st.markdown("### Quality by Remoteness — the remote paradox")
        mmm_present = [m for m in MMM_ORDER if m in df['mmm_code'].values]
        if mmm_present:
            mmm_df = (
                df.groupby('mmm_code', observed=True)['quality_score']
                .mean()
                .reset_index()
            )
            mmm_df['mmm_code'] = pd.Categorical(mmm_df['mmm_code'], categories=MMM_ORDER, ordered=True)
            mmm_df = mmm_df.sort_values('mmm_code')
            mmm_df['label'] = mmm_df['mmm_code'].map(MMM_LABELS).fillna(mmm_df['mmm_code'])
            mmm_df['colour'] = mmm_df['mmm_code'].map(MMM_COLOURS)
            fig_mmm = px.bar(
                mmm_df, x='label', y='quality_score',
                color='mmm_code',
                color_discrete_map=MMM_COLOURS,
                text='quality_score',
                title=f'Average Quality Score by Remoteness Band ({year_sel})',
                labels={'quality_score': 'Avg Quality Score ★', 'label': 'Remoteness Band', 'mmm_code': 'Band'},
            )
            fig_mmm.update_traces(texttemplate='%{text:.2f}★', textposition='outside')
            fig_mmm.update_layout(showlegend=False)
            theme(fig_mmm, height=380)
            st.plotly_chart(fig_mmm, use_container_width=True)
        st.info(
            "**Counterintuitive:** Remote and very remote areas score *higher* on quality — "
            "MM7 averages **3.90★** vs MM1 (major cities) at **3.55★**. "
            "The remote disadvantage is **access** (fewer beds, longer distances), not quality of care."
        )

        # --- State CGI bar chart ---
        st.markdown("### Care Gap by State — who's under most pressure?")
        state_df = (
            df.groupby('state', observed=True)['care_gap_index']
            .mean()
            .reset_index()
            .sort_values('care_gap_index', ascending=True)
        )
        fig_state = px.bar(
            state_df, x='care_gap_index', y='state', orientation='h',
            color='care_gap_index',
            color_continuous_scale=[[0, C['bg']], [0.5, '#4A7FC1'], [1, C['navy']]],
            text='care_gap_index',
            title=f'Average Care Gap Index by State/Territory ({year_sel})',
            labels={'care_gap_index': 'Avg Care Gap Index', 'state': ''},
        )
        fig_state.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_state.update_layout(coloraxis_showscale=False)
        theme(fig_state, height=400)
        st.plotly_chart(fig_state, use_container_width=True)
        st.success(
            "ACT has the highest residential access rate (**5.01%** of 65+) — driven by concentrated demand, "
            "not better supply. In 2023→2024, **250 SA3s (79%)** saw their care gap improve. "
            "The 21% that worsened are concentrated in major city (MM1) regions."
        )
