"""
Australia's Aged Care Gap — DVN AT3 Dashboard
Streamlit app | 4 tabs | 3 advanced features

Advanced features:
  1. Context-aware filtering: sidebar filters update all charts + narrative text dynamically
  2. Visual tooltips: hover on any chart shows SA3-level detail (name, state, all metrics)
  3. What-if parameterisation: slider "If beds_per_1k reaches X, how many SA3s exit the red zone?"

Data: data/clean/master_sa3.csv + data/clean/star_ratings_by_facility.csv
      data/raw/abs_geography/SA3_2021_AUST_GDA2020.shp
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Australia's Aged Care Gap",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE  = os.path.dirname(os.path.abspath(__file__))
CLEAN = os.path.join(BASE, '..', 'data', 'clean')
GEO   = os.path.join(BASE, '..', 'data', 'raw', 'abs_geography')

# ── Colour palette ────────────────────────────────────────────────────────────
COLOUR = {
    'red':    '#da1e28',
    'orange': '#ff832b',
    'yellow': '#f1c21b',
    'green':  '#24a148',
    'blue':   '#0f62fe',
    'muted':  '#6f6f6f',
}
MMM_COLOURS = {
    'MM1':'#0f62fe','MM2':'#ff832b','MM3':'#24a148',
    'MM4':'#da1e28','MM5':'#9467bd','MM6':'#8c564b','MM7':'#e377c2'
}
ORG_COLOURS = {
    'profit':         '#da1e28',
    'not_for_profit': '#0f62fe',
    'government':     '#24a148',
}

# ── Data loading (cached) ─────────────────────────────────────────────────────
@st.cache_data
def load_master():
    return pd.read_csv(os.path.join(CLEAN, 'master_sa3.csv'))

@st.cache_data
def load_ratings():
    return pd.read_csv(
        os.path.join(CLEAN, 'star_ratings_by_facility.csv'),
        parse_dates=['snapshot_date']
    )

@st.cache_data
def load_users():
    return pd.read_csv(os.path.join(CLEAN, 'service_users_by_sa3.csv'))

@st.cache_data
def load_funding():
    return pd.read_csv(os.path.join(CLEAN, 'service_funding_by_facility.csv'))

@st.cache_data
def load_shapefile():
    shp = os.path.join(GEO, 'SA3_2021_AUST_GDA2020.shp')
    if not os.path.exists(shp):
        return None
    gdf = gpd.read_file(shp)
    gdf = gdf.rename(columns={'SA3_CODE21': 'sa3_code'})
    gdf['sa3_code'] = pd.to_numeric(gdf['sa3_code'], errors='coerce').astype('Int64')
    return gdf

master  = load_master()
ratings = load_ratings()
users   = load_users()
funding = load_funding()
gdf     = load_shapefile()

# ── Snap year mapping ─────────────────────────────────────────────────────────
SNAP_YEAR = {
    'May 2023':2023,'August 2023':2023,'December 2023':2023,
    'February 2024':2024,'May 2024':2024,'July 2024':2024,'November 2024':2024,
    'February 2025':2025,'May 2025':2025,'August 2025':2025,'October 2025':2025,
    'February 2026':2026,
}
ratings['snap_year'] = ratings['snapshot'].map(SNAP_YEAR)
ratings['org_type']  = ratings['Purpose'].str.strip().str.lower().map({
    'for profit':'profit','not for profit':'not_for_profit','government':'government'
}).fillna('unknown')
MANDATE = pd.Timestamp('2023-10-01')

# ── Sidebar — ADVANCED FEATURE 1: Context-aware filtering ─────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/3/30/UTS_logo.svg/240px-UTS_logo.svg.png",
             width=80)
    st.title("Australia's Aged Care Gap")
    st.caption("DVN AT3 · UTS MDSI Autumn 2026")
    st.divider()

    st.subheader("🔍 Filters")
    st.caption("Selections update all tabs dynamically")

    # Year filter
    year_sel = st.radio(
        "Year",
        options=[2023, 2024],
        index=1,
        horizontal=True,
        help="access_rate is only computable for 2023 and 2024"
    )

    # State filter
    states = sorted(master['state'].dropna().unique())
    state_sel = st.multiselect(
        "State / Territory",
        options=states,
        default=states,
        help="Filter all charts by state"
    )

    # Remoteness filter
    mmm_opts = sorted(master['mmm_code'].dropna().unique())
    mmm_sel = st.multiselect(
        "Remoteness (MMM)",
        options=mmm_opts,
        default=mmm_opts,
        help="MM1 = Major City … MM7 = Very Remote"
    )

    st.divider()

    # ADVANCED FEATURE 3: What-if parameterisation
    st.subheader("💡 What-If Scenario")
    st.caption("If all SA3s reached this beds_per_1k target, how many exit the red zone?")
    whatif_target = st.slider(
        "Target beds per 1,000 elderly",
        min_value=30.0,
        max_value=80.0,
        value=50.0,
        step=1.0,
    )

    st.divider()
    st.caption("Data: GEN aged care data & ABS 2021–2026")
    st.caption("Project brief: `DVN_AT3_Aged_Care_Gap_Australia.html`")

# ── Filter master by sidebar selections ───────────────────────────────────────
df = master[
    (master['year'] == year_sel) &
    (master['state'].isin(state_sel)) &
    (master['mmm_code'].isin(mmm_sel))
].copy()

# Context-aware narrative text (updates with filters)
n_sa3       = df['sa3_code'].nunique()
n_deficit   = (df.drop_duplicates('sa3_name')['waitlist_pressure'] > 1.0).sum()
med_quality = df['quality_score'].median()
med_cgi     = df['care_gap_index'].median()

# ── KPI banner (context-aware) ────────────────────────────────────────────────
st.markdown(f"""
# 🏥 Australia's Aged Care Gap
**Which regions have the worst gap between quality and access — and why?**
""")

k1, k2, k3, k4 = st.columns(4)
k1.metric("SA3 Regions", f"{n_sa3}", help="Regions matching current filter")
k2.metric("In Deficit", f"{n_deficit}",
          help="Regions where high-needs HCP > residential beds (pressure > 1.0)")
k3.metric("Median Quality Score", f"{med_quality:.2f}",
          help="Mean of 4 ACQSC star rating sub-dimensions")
k4.metric("Median Care Gap Index", f"{med_cgi:.2f}",
          help="access_rate / quality_score — higher = more underserved")

st.divider()

# ── 4 Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Ch 1 — The Map",
    "📊 Ch 2 — The Correlation",
    "🚨 Ch 3 — The Reveal",
    "📈 Ch 4 — Mandate Effect",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — THE MAP
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("The Map: Is aged care near me any good?")
    st.markdown(
        "Each SA3 is coloured by **care_gap_index** — the ratio of access rate to quality score. "
        "Darker red = more underserved. Two patterns emerge: high-access/low-quality metro areas "
        "and low-access/high-quality remote areas."
    )

    if gdf is not None:
        # Join shapefile with filtered master
        merged = gdf.merge(df[['sa3_code','sa3_name','state','mmm_code',
                                'care_gap_index','quality_score','access_rate',
                                'waitlist_pressure','pop_65_plus']],
                           on='sa3_code', how='left')
        merged = merged.to_crs(epsg=4326)

        fig_map = px.choropleth(
            merged,
            geojson=merged.__geo_interface__,
            locations=merged.index,
            color='care_gap_index',
            color_continuous_scale='YlOrRd',
            range_color=[0, df['care_gap_index'].quantile(0.95)],
            hover_data={
                'sa3_name':       True,
                'state':          True,
                'mmm_code':       True,
                'care_gap_index': ':.2f',
                'quality_score':  ':.2f',
                'access_rate':    ':.1f',
                'pop_65_plus':    ':,.0f',
            },
            title=f'Care Gap Index by SA3 ({year_sel}) — darker = more underserved',
            labels={'care_gap_index': 'Care Gap Index'}
        )
        fig_map.update_geos(fitbounds='locations', visible=False)
        fig_map.update_layout(height=550, margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning(
            "Shapefile not found at `data/raw/abs_geography/SA3_2021_AUST_GDA2020.shp`. "
            "Download from ABS ASGS 2021 and extract to that folder."
        )
        # Fallback: scatter map using lat/long approximation from sa3_code
        st.info("Showing bubble chart as fallback (no shapefile required).")
        fig_fallback = px.scatter(
            df.dropna(subset=['care_gap_index','quality_score']),
            x='access_rate', y='quality_score',
            color='care_gap_index',
            size='pop_65_plus',
            hover_name='sa3_name',
            hover_data={'state':True,'mmm_code':True,'care_gap_index':':.2f'},
            color_continuous_scale='YlOrRd',
            title=f'Access rate vs quality score ({year_sel}) — coloured by care gap index',
            labels={'access_rate':'Access rate (%)','quality_score':'Quality score'}
        )
        st.plotly_chart(fig_fallback, use_container_width=True)

    # Top/bottom 10 table
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🔴 Top 10 most underserved SA3s**")
        top10 = df.nlargest(10,'care_gap_index')[
            ['sa3_name','state','mmm_code','care_gap_index','access_rate','quality_score']
        ].round(3).reset_index(drop=True)
        st.dataframe(top10, use_container_width=True, hide_index=True)
    with c2:
        st.markdown("**🟢 Top 10 best served SA3s**")
        bot10 = df.nsmallest(10,'care_gap_index')[
            ['sa3_name','state','mmm_code','care_gap_index','access_rate','quality_score']
        ].round(3).reset_index(drop=True)
        st.dataframe(bot10, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — THE CORRELATION
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("The Correlation: Who runs the best facilities?")
    st.markdown(
        "Quality differences are not explained by geography — they are explained by **ownership**. "
        "Government facilities average 4.21 vs for-profit 3.68 (gap = 0.53 pts). "
        "Remote areas score higher *because* they have fewer for-profit providers."
    )

    c1, c2 = st.columns([2, 1])

    with c1:
        # Scatter: access_rate vs quality_score
        scatter_df = df.dropna(subset=['access_rate','quality_score','mmm_code','pop_65_plus'])
        fig_scatter = px.scatter(
            scatter_df,
            x='access_rate', y='quality_score',
            size='pop_65_plus',
            color='mmm_code',
            color_discrete_map=MMM_COLOURS,
            hover_name='sa3_name',
            hover_data={
                'state':True,'mmm_code':True,
                'access_rate':':.2f','quality_score':':.3f',
                'care_gap_index':':.2f','pop_65_plus':':,.0f'
            },
            trendline='ols',
            size_max=30,
            title=f'Access rate vs quality score ({year_sel})<br>'
                  '<sup>Pearson r ≈ −0.08 — ownership type, not geography, explains quality</sup>',
            labels={
                'access_rate':   'Access rate (% of 65+ in residential care)',
                'quality_score': 'Quality score (avg of 4 ACQSC sub-dimensions)',
                'mmm_code':      'Remoteness'
            }
        )
        fig_scatter.update_layout(height=450)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c2:
        # Quality by org type — latest snapshot
        latest = ratings[ratings['snapshot_date'] == ratings['snapshot_date'].max()]
        latest = latest[latest['org_type'] != 'unknown']
        org_q  = latest.groupby('org_type')['quality_score'].mean().reset_index()
        fig_org = px.bar(
            org_q.sort_values('quality_score', ascending=True),
            x='quality_score', y='org_type',
            orientation='h',
            color='org_type',
            color_discrete_map=ORG_COLOURS,
            text='quality_score',
            title='Avg quality by org type<br><sup>Feb 2026 snapshot</sup>',
            labels={'quality_score':'Quality score','org_type':'Org type'}
        )
        fig_org.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_org.update_layout(height=250, showlegend=False)
        st.plotly_chart(fig_org, use_container_width=True)

        # Org type mix by MMM
        mmm_org = (latest.groupby(['mmm_code','org_type']).size().reset_index(name='n'))
        mmm_org['pct'] = mmm_org.groupby('mmm_code')['n'].transform(
            lambda x: x / x.sum() * 100)
        fig_mmm_org = px.bar(
            mmm_org,
            x='mmm_code', y='pct', color='org_type',
            color_discrete_map=ORG_COLOURS,
            barmode='stack',
            title='Org type mix by remoteness<br><sup>For-profit = 42% in MM1, 0% in MM6–7</sup>',
            labels={'pct':'% of facilities','mmm_code':'Remoteness','org_type':'Org type'}
        )
        fig_mmm_org.update_layout(height=200, showlegend=False)
        st.plotly_chart(fig_mmm_org, use_container_width=True)

    # Funding bar chart
    st.markdown("---")
    st.markdown("**Government funding by org type — for-profit receives more per facility despite lower quality**")
    fund_trend = (funding[funding['funding'] > 0]
                  .groupby(['year','org_type'])['funding'].sum().reset_index())
    fund_trend['funding_bn'] = fund_trend['funding'] / 1e9
    fig_fund = px.bar(
        fund_trend, x='year', y='funding_bn', color='org_type',
        color_discrete_map=ORG_COLOURS,
        barmode='stack',
        title='Government funding by org type ($B) — 2019–2025',
        labels={'funding_bn':'Funding ($B)','org_type':'Org type'}
    )
    st.plotly_chart(fig_fund, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — THE REVEAL
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("The Reveal: Which communities are being left behind?")

    # Context-aware narrative text (updates with filter)
    worst = df.drop_duplicates('sa3_name').nlargest(1,'waitlist_pressure').iloc[0]
    st.markdown(
        f"In **{year_sel}**, **{n_deficit} SA3 regions** have more high-needs home care users "
        f"than available residential beds. The worst is **{worst['sa3_name']} ({worst['state']})** "
        f"with a pressure ratio of **{worst['waitlist_pressure']:.2f}** — "
        f"{int(worst['hcp_high_needs'])} people competing for {int(worst['residential_places'])} beds."
    )

    # Top 20 bar chart
    top20 = (df.nlargest(30,'waitlist_pressure')
               .drop_duplicates('sa3_name')
               .head(20)
               .sort_values('waitlist_pressure'))

    fig_wp = px.bar(
        top20,
        x='waitlist_pressure', y='sa3_name',
        color='mmm_code',
        color_discrete_map=MMM_COLOURS,
        orientation='h',
        hover_data={
            'state':True,'hcp_high_needs':':,d',
            'residential_places':':,d','waitlist_pressure':':.3f',
            'access_rate':':.2f','quality_score':':.3f','pop_65_plus':':,.0f'
        },
        title=f'Top 20 SA3 regions by waitlist pressure ({year_sel})<br>'
              '<sup>HCP high-needs (L3+L4) per available residential bed — '
              'red line = demand equals supply</sup>',
        labels={
            'waitlist_pressure':'High-needs HCP per residential bed',
            'sa3_name':'','mmm_code':'Remoteness'
        }
    )
    fig_wp.add_vline(x=1.0, line_dash='dash', line_color='red', line_width=2,
                     annotation_text='Demand = Supply', annotation_position='top right')
    fig_wp.update_layout(height=520)
    st.plotly_chart(fig_wp, use_container_width=True)

    # HCP stacked bar
    hcp_melt = top20.melt(
        id_vars=['sa3_name','waitlist_pressure'],
        value_vars=['hcp_level1','hcp_level2','hcp_level3','hcp_level4'],
        var_name='level', value_name='users'
    )
    hcp_melt['level_label'] = hcp_melt['level'].map({
        'hcp_level1':'L1 — Basic','hcp_level2':'L2 — Moderate',
        'hcp_level3':'L3 — High (near-residential)',
        'hcp_level4':'L4 — Very High (should be in residential)'
    })
    sa3_order = top20['sa3_name'].tolist()
    fig_hcp = px.bar(
        hcp_melt,
        x='sa3_name', y='users', color='level_label',
        category_orders={
            'sa3_name':sa3_order,
            'level_label':['L1 — Basic','L2 — Moderate',
                           'L3 — High (near-residential)',
                           'L4 — Very High (should be in residential)']
        },
        color_discrete_map={
            'L1 — Basic':'#a6c8ff','L2 — Moderate':'#4589ff',
            'L3 — High (near-residential)':'#ff832b',
            'L4 — Very High (should be in residential)':'#da1e28'
        },
        barmode='stack',
        title='HCP level composition — who is actually waiting?',
        labels={'users':'Home care users','sa3_name':'','level_label':'Care level'}
    )
    fig_hcp.update_layout(height=400, xaxis_tickangle=45)
    st.plotly_chart(fig_hcp, use_container_width=True)

    # ADVANCED FEATURE 3: What-if result
    st.markdown("---")
    st.markdown(f"### 💡 What-If: beds_per_1k target = **{whatif_target:.0f}**")
    current_red   = (df['care_gap_index'] > df['care_gap_index'].median()).sum()
    would_improve = (df['beds_per_1k'] < whatif_target).sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("Current SA3s below target", f"{would_improve}",
                help=f"SA3s currently below {whatif_target:.0f} beds per 1,000 elderly")
    col2.metric("Currently above target", f"{len(df) - would_improve}",
                help="SA3s already at or above the target")
    col3.metric(
        "National avg beds/1k",
        f"{(df['residential_places'].sum()/df['pop_65_plus'].sum()*1000):.1f}",
        help="Current national average"
    )
    fig_whatif = px.histogram(
        df, x='beds_per_1k', nbins=30,
        color_discrete_sequence=[COLOUR['blue']],
        title=f'Distribution of beds per 1,000 elderly — target line at {whatif_target:.0f}',
        labels={'beds_per_1k':'Beds per 1,000 elderly'}
    )
    fig_whatif.add_vline(x=whatif_target, line_dash='dash', line_color='red',
                         annotation_text=f'Target: {whatif_target:.0f}',
                         annotation_position='top right')
    fig_whatif.update_layout(height=300)
    st.plotly_chart(fig_whatif, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — MANDATE EFFECT
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Mandate Effect: Did the Oct 2023 staffing mandate work?")
    st.markdown(
        "**Yes — but only for inputs, not outcomes.** "
        "National quality rose +0.25 pts (3.40 → 3.65, +7.3%) after Oct 2023. "
        "Staffing sub-rating jumped +0.51 pts — the largest gain. "
        "But quality measures (resident health outcomes) are flat at −0.015 pts. "
        "The mandate fixed staff hours; it has not yet fixed care."
    )

    # Quality over time
    nat_time = ratings.groupby('snapshot_date')['quality_score'].mean().reset_index()
    fig_time = px.line(
        nat_time, x='snapshot_date', y='quality_score',
        title='National average quality score over time — mandate Oct 2023',
        labels={'quality_score':'Avg quality score','snapshot_date':'Quarter'}
    )
    fig_time.add_vline(
        x=MANDATE.timestamp() * 1000,
        line_dash='dash', line_color='red',
        annotation_text='Oct 2023 mandate',
        annotation_position='top left'
    )
    fig_time.update_layout(height=350)
    st.plotly_chart(fig_time, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        # Sub-rating before vs after
        ratings['period'] = ratings['snapshot_date'].apply(
            lambda d: 'After mandate' if d >= MANDATE else 'Before mandate'
        )
        dims = ['residents_exp','staffing','compliance','quality_measures']
        labels = ['Residents exp.','Staffing','Compliance','Quality measures']
        before = ratings[ratings['period']=='Before mandate'][dims].mean()
        after  = ratings[ratings['period']=='After mandate'][dims].mean()
        sub_df = pd.DataFrame({
            'Sub-rating': labels,
            'Before': before.values,
            'After':  after.values
        })
        sub_melt = sub_df.melt(id_vars='Sub-rating', var_name='Period', value_name='Score')
        fig_sub = px.bar(
            sub_melt, x='Sub-rating', y='Score', color='Period',
            barmode='group',
            color_discrete_map={'Before':'#8d8d8d','After':'#0f62fe'},
            title='Sub-rating change before vs after mandate',
            labels={'Score':'Avg score'}
        )
        fig_sub.update_layout(height=350)
        st.plotly_chart(fig_sub, use_container_width=True)

    with c2:
        # Quality by org type over time
        org_time = (ratings[ratings['org_type']!='unknown']
                    .groupby(['snapshot_date','org_type'])['quality_score']
                    .mean().reset_index())
        fig_org_time = px.line(
            org_time, x='snapshot_date', y='quality_score',
            color='org_type',
            color_discrete_map=ORG_COLOURS,
            title='Quality by org type over time',
            labels={'quality_score':'Avg quality score',
                    'snapshot_date':'Quarter','org_type':'Org type'}
        )
        fig_org_time.add_vline(
            x=MANDATE.timestamp() * 1000,
            line_dash='dash', line_color='red'
        )
        fig_org_time.update_layout(height=350)
        st.plotly_chart(fig_org_time, use_container_width=True)

    # Compliance trend
    post_mandate = ratings[ratings['snapshot_date'] >= MANDATE]
    comp_time = (post_mandate.dropna(subset=['fully_compliant'])
                 .groupby('snapshot_date')['fully_compliant']
                 .mean().reset_index())
    comp_time['pct'] = comp_time['fully_compliant'] * 100
    fig_comp = px.line(
        comp_time, x='snapshot_date', y='pct',
        title='% of facilities fully compliant with staffing minutes — post-mandate',
        labels={'pct':'% fully compliant','snapshot_date':'Quarter'}
    )
    fig_comp.add_hline(y=65, line_dash='dot', line_color='green',
                       annotation_text='65% target', annotation_position='top right')
    fig_comp.update_layout(height=300)
    st.plotly_chart(fig_comp, use_container_width=True)

