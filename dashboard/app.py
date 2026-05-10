"""
Australia's Aged Care Gap — DVN AT3 Dashboard
Design system: blue-spectrum / teal / gold / cream / care-gap-red
Navigation: query-param routing (?page=home|map|correlation|reveal|mandate)
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import base64
import os
import sys

# ── Make tabs/ importable ──────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from tabs.utils import C, MMM_COLOURS, ORG_COLOURS, SNAP_YEAR, MANDATE
import tabs.home           as pg_home
import tabs.ch1_map        as pg_map
import tabs.ch2_correlation as pg_corr
import tabs.ch3_reveal     as pg_reveal
import tabs.ch4_mandate    as pg_mandate

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Australia's Aged Care Gap",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ──────────────────────────────────────────────────────────────────────
CLEAN  = os.path.join(BASE, '..', 'data', 'clean')
GEO    = os.path.join(BASE, '..', 'data', 'raw', 'abs_geography')
ASSETS = (os.path.join(BASE, 'assets')
          if os.path.isdir(os.path.join(BASE, 'assets'))
          else os.path.join(BASE, '..', 'notebooks', 'artist', 'assets'))

# ── Helpers ────────────────────────────────────────────────────────────────────
@st.cache_data
def _b64(path: str) -> str:
    if not os.path.exists(path):
        return ''
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()


# ── Data loading (cached) ──────────────────────────────────────────────────────
@st.cache_data
def load_master():
    return pd.read_csv(os.path.join(CLEAN, 'master_sa3.csv'))


@st.cache_data
def load_ratings():
    df = pd.read_csv(
        os.path.join(CLEAN, 'star_ratings_by_facility.csv'),
        parse_dates=['snapshot_date'],
    ).copy()
    df['snap_year'] = df['snapshot'].map(SNAP_YEAR)
    df['org_type'] = (
        df['Purpose'].str.strip().str.lower()
        .map({'for profit': 'profit', 'not for profit': 'not_for_profit', 'government': 'government'})
        .fillna('unknown')
    )
    df['period'] = df['snapshot_date'].apply(
        lambda d: 'After mandate' if d >= MANDATE else 'Before mandate'
    )
    return df


@st.cache_data
def load_funding():
    return pd.read_csv(os.path.join(CLEAN, 'service_funding_by_facility.csv'))


@st.cache_resource
def load_shapefile():
    shp = os.path.join(GEO, 'SA3_2021_AUST_GDA2020.shp')
    if not os.path.exists(shp):
        return None
    gdf = gpd.read_file(shp)
    gdf = gdf.rename(columns={'SA3_CODE21': 'sa3_code'})
    gdf['sa3_code'] = pd.to_numeric(gdf['sa3_code'], errors='coerce').astype('Int64')
    gdf = gdf.to_crs(epsg=4326)
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01, preserve_topology=True)
    return gdf


master  = load_master()
ratings = load_ratings()
funding = load_funding()
gdf     = load_shapefile()

hero_b64 = _b64(os.path.join(ASSETS, 'img-landing-bg.jpg'))
ico_b64  = _b64(os.path.join(ASSETS, 'ico-dashboard.png'))

# ── CSS ────────────────────────────────────────────────────────────────────────
NAV_H = 64
CSS = f"""<style>
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ display: none !important; }}
.stDeployButton, div[data-testid="stToolbar"] {{ display: none !important; }}

.stApp, section[data-testid="stAppViewContainer"] {{ background: {C['bg']}; }}

.main .block-container {{
    padding-top: {NAV_H + 16}px !important;
    padding-bottom: 56px !important;
    max-width: 1380px;
}}

section[data-testid="stSidebar"] {{
    background: {C['white']} !important;
    border-right: 1px solid {C['border']};
}}
section[data-testid="stSidebar"] > div:first-child {{ padding-top: 1.5rem !important; }}

section[data-testid="stSidebar"] details[data-testid="stExpander"] {{
    background: transparent !important; border: none !important;
    border-bottom: 1px solid {C['border']} !important;
    border-radius: 0 !important; margin: 0 0 6px !important;
}}
section[data-testid="stSidebar"] details[data-testid="stExpander"] summary {{
    background: {C['navy']} !important; color: white !important;
    border-radius: 8px !important; font-weight: 600 !important;
    font-size: 0.88rem !important; padding: 10px 14px !important;
}}
section[data-testid="stSidebar"] details[data-testid="stExpander"][open] summary {{
    border-radius: 8px 8px 0 0 !important;
}}
section[data-testid="stSidebar"] details[data-testid="stExpander"] > div[data-testid="stExpanderDetails"] {{
    background: {C['light']} !important; border: 1px solid {C['border']};
    border-top: none; border-radius: 0 0 8px 8px; padding: 12px 10px !important;
}}
section[data-testid="stSidebar"] details summary svg {{ fill: white !important; }}

.stPlotlyChart {{
    background: {C['white']}; border-radius: 12px;
    border: 1px solid {C['border']}; padding: 4px;
}}

.stTextInput input {{
    border-radius: 24px !important; border: 1px solid {C['border']} !important;
    padding: 8px 20px !important; background: {C['white']} !important;
}}
.stTextInput label {{ color: {C['navy']} !important; font-weight: 700 !important; font-size: 0.95rem !important; }}

.stSlider [data-baseweb="slider"] [role="slider"] {{
    background-color: {C['teal']} !important; border-color: {C['teal']} !important;
}}
.stSlider [data-baseweb="track"] [data-testid="stSliderTrackFill"] {{
    background-color: {C['teal']} !important;
}}

[data-testid="stMetric"] {{
    background: {C['white']}; border: 1px solid {C['border']};
    border-radius: 12px; padding: 16px 20px;
}}
[data-testid="stMetricLabel"] {{ color: {C['teal']} !important; font-weight: 700 !important; }}
[data-testid="stMetricValue"] {{ color: {C['navy']} !important; }}

.nav-bar {{
    position: fixed; top: 0; left: calc(21rem - 16px); right: 0;
    height: {NAV_H}px; background: {C['navy']};
    display: flex; align-items: center; padding: 0 28px;
    z-index: 9999; box-shadow: 0 2px 12px rgba(0,0,0,0.18);
    border-radius: 0 0 10px 10px; margin: 0 10px 0 0;
}}
.nav-bar a {{ text-decoration: none !important; }}
.nav-home-btn {{
    color: white; padding: 6px 18px; border-radius: 6px;
    font-weight: 700; font-size: 14px; white-space: nowrap;
    cursor: pointer; transition: background 0.15s; display: inline-block;
}}
.nav-home-btn:hover, .nav-home-btn.active {{ background: {C['teal']}; color: white !important; }}

.nav-chapters {{
    display: flex; align-items: flex-end; margin-left: auto;
    position: relative; padding-top: 18px; gap: 0;
}}
.nav-chapters::before {{
    content: ''; position: absolute; top: 7px; left: 24px; right: 24px;
    height: 2px; background: rgba(255,255,255,0.85); pointer-events: none;
}}
.nav-ch {{ position: relative; padding: 0 4px; }}
.nav-ch::before {{
    content: ''; position: absolute; top: -14px; left: 50%;
    transform: translateX(-50%); width: 8px; height: 8px;
    border-radius: 50%; background: rgba(255,255,255,0.85); z-index: 1;
}}
.nav-ch.active::before {{ background: {C['teal']}; box-shadow: 0 0 0 3px rgba(0,167,157,0.3); }}
.nav-ch-link {{
    display: block; color: white !important; font-size: 13px;
    padding: 5px 14px; border-radius: 6px; white-space: nowrap; transition: all 0.15s;
}}
.nav-ch-link:hover {{ color: white !important; background: rgba(255,255,255,0.1); }}
.nav-ch.active .nav-ch-link {{ background: {C['teal']}; color: white !important; font-weight: 600; }}

.kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 0 0 8px; }}
.kpi-card {{
    background: {C['white']}; border: 1px solid {C['border']};
    border-radius: 12px; padding: 20px 24px 18px;
}}
.kpi-label {{
    color: {C['teal']}; font-weight: 700; font-size: 0.78rem;
    letter-spacing: 0.04em; text-transform: uppercase;
    display: flex; align-items: center; gap: 6px; margin-bottom: 10px;
}}
.kpi-help {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 15px; height: 15px; background: {C['border']}; border-radius: 50%;
    font-size: 9px; color: {C['muted']}; font-weight: 700;
    position: relative; cursor: help;
}}
.kpi-help::after {{
    content: attr(data-tooltip); position: absolute;
    bottom: calc(100% + 8px); left: 50%; transform: translateX(-50%);
    background: {C['navy']}; color: white; padding: 7px 13px;
    border-radius: 8px; font-size: 0.76rem; font-weight: 400;
    white-space: nowrap; opacity: 0; pointer-events: none;
    transition: opacity 0.18s; z-index: 99999; box-shadow: 0 4px 14px rgba(0,0,0,0.18);
}}
.kpi-help::before {{
    content: ''; position: absolute; bottom: calc(100% + 2px); left: 50%;
    transform: translateX(-50%); border: 5px solid transparent;
    border-top-color: {C['navy']}; opacity: 0; pointer-events: none;
    transition: opacity 0.18s; z-index: 99999;
}}
.kpi-help:hover::after, .kpi-help:hover::before {{ opacity: 1; }}
.kpi-value {{ color: {C['navy']}; font-size: 2.4rem; font-weight: 800; line-height: 1; }}
.kpi-suffix {{ font-size: 1rem; color: {C['muted']}; font-weight: 500; }}

.sec-h1 {{ color: {C['navy']}; font-size: 2.2rem; font-weight: 800; margin-bottom: 10px; line-height: 1.2; }}
.sec-p {{ color: {C['muted']}; font-size: 0.95rem; margin-bottom: 20px; line-height: 1.65; max-width: 900px; }}
.sub-h {{ color: {C['navy']}; font-size: 1.05rem; font-weight: 700; margin: 24px 0 8px; }}

.hero-wrap {{
    border-radius: 16px; overflow: hidden; margin-bottom: 28px;
    min-height: 480px; display: flex; align-items: center;
    justify-content: center; position: relative;
}}
.hero-inner {{ text-align: center; color: white; padding: 64px 48px; position: relative; z-index: 1; }}
.hero-h {{ font-size: 2.55rem; font-weight: 800; line-height: 1.25; margin-bottom: 32px; text-shadow: 0 2px 8px rgba(0,0,0,0.3); }}
.hero-btn {{
    display: inline-block; background: {C['teal']}; color: white !important;
    text-decoration: none !important; padding: 16px 48px; border-radius: 40px;
    font-size: 1.1rem; font-weight: 700; transition: background 0.2s, transform 0.1s;
    box-shadow: 0 4px 16px rgba(0,167,157,0.35);
}}
.hero-btn:hover {{ background: #007A72; transform: translateY(-1px); }}

.nb-card {{
    background: {C['white']}; border: 1.5px solid {C['teal']};
    border-radius: 10px; padding: 14px 20px; margin-bottom: 16px;
    color: {C['navy']}; font-size: 0.95rem;
}}

.whatif-box {{
    background: {C['light']}; border: 1px solid {C['border']};
    border-radius: 12px; padding: 20px 24px; margin: 28px 0 16px;
}}
.whatif-title {{ color: {C['navy']}; font-size: 1.1rem; font-weight: 700; margin-bottom: 4px; }}
.whatif-sub {{ color: {C['muted']}; font-size: 0.87rem; margin-bottom: 0; }}

.data-caption {{ color: {C['muted']}; font-size: 0.8rem; font-style: italic; margin-top: 28px; }}

span[data-baseweb="tag"] {{
    background-color: {C['navy']} !important; border-color: {C['navy']} !important;
    border-radius: 4px !important;
}}
span[data-baseweb="tag"] span {{ color: white !important; }}
span[data-baseweb="tag"] button span svg {{ fill: rgba(255,255,255,0.75) !important; }}

div[data-baseweb="radio"] div[role="radio"][aria-checked="true"] {{
    background-color: {C['teal']} !important; border-color: {C['teal']} !important;
}}
div[data-baseweb="radio"] div[role="radio"][aria-checked="true"] > div {{ background-color: white !important; }}
div[data-baseweb="radio"]:hover div[role="radio"] {{ border-color: {C['teal']} !important; }}

li[role="option"] span[data-baseweb="checkbox"] > div {{ border-color: {C['teal']} !important; }}
li[role="option"][aria-selected="true"] span[data-baseweb="checkbox"] > div {{
    background-color: {C['teal']} !important; border-color: {C['teal']} !important;
}}
</style>"""

st.markdown(CSS, unsafe_allow_html=True)

# ── Navigation bar ─────────────────────────────────────────────────────────────
page = st.query_params.get("page", "home")

NAV_CHAPTERS = [
    ("Chapter 1: The Map",         "map"),
    ("Chapter 2: The Correlation", "correlation"),
    ("Chapter 3: The Reveal",      "reveal"),
    ("Chapter 4: Mandate Effect",  "mandate"),
]
ch_html = "".join(
    f'<div class="nav-ch {"active" if page == k else ""}">'
    f'<a class="nav-ch-link" href="?page={k}" target="_self">{lbl}</a>'
    f'</div>'
    for lbl, k in NAV_CHAPTERS
)
st.markdown(
    f'<div class="nav-bar">'
    f'<a href="?page=home" target="_self">'
    f'<span class="nav-home-btn {"active" if page == "home" else ""}">Home</span>'
    f'</a>'
    f'<div class="nav-chapters">{ch_html}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    if ico_b64:
        st.markdown(
            f'<a href="?page=home" target="_self" style="display:inline-block;margin-bottom:12px">'
            f'<img src="data:image/png;base64,{ico_b64}" width="52"'
            f' style="display:block;cursor:pointer;'
            f'filter:brightness(0) saturate(100%) invert(53%) sepia(68%) saturate(380%)'
            f' hue-rotate(136deg) brightness(90%);">'
            f'</a>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<p style="margin:0;color:{C["navy"]};font-size:1.05rem;font-weight:800;line-height:1.2">'
        f'Australia Aged Care Gap</p>'
        f'<p style="margin:3px 0 0;color:{C["muted"]};font-size:0.78rem">'
        f'by DVN AT3 — UTS MDSI Autumn 2026</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<hr style="border:none;border-top:1px solid {C["border"]};margin:16px 0 12px">',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="margin:0 0 2px;color:{C["navy"]};font-weight:700;font-size:1rem">'
        f'Global Filter</p>'
        f'<p style="margin:0 0 14px;color:{C["muted"]};font-size:0.78rem">'
        f'Selections update all tabs dynamically</p>',
        unsafe_allow_html=True,
    )

    with st.expander("Year", expanded=True):
        year_sel = st.radio("Year", [2023, 2024], index=1,
                            horizontal=True, label_visibility="collapsed")

    with st.expander("State / Territory"):
        states = sorted(master['state'].dropna().unique())
        state_sel = st.multiselect("State", states, default=states,
                                   label_visibility="collapsed")

    with st.expander("Remoteness (MMM)"):
        mmm_opts = sorted(master['mmm_code'].dropna().unique())
        mmm_sel = st.multiselect("MMM", mmm_opts, default=mmm_opts,
                                 label_visibility="collapsed")

# ── Filter slices ──────────────────────────────────────────────────────────────
_states = state_sel if state_sel else states
_mmm    = mmm_sel   if mmm_sel   else mmm_opts

df = master[
    (master['year'] == year_sel) &
    (master['state'].isin(_states)) &
    (master['mmm_code'].isin(_mmm))
].copy()

# ── KPI values (computed once, shared across pages) ────────────────────────────
n_sa3       = df['sa3_code'].nunique()
n_deficit   = int((df.drop_duplicates('sa3_name')['waitlist_pressure'] > 1.0).sum()) if not df.empty else 0
med_quality = round(float(df['quality_score'].median()), 2) if not df.empty else 0.0
med_cgi     = round(float(df['care_gap_index'].median()), 2) if not df.empty else 0.0

KPI_HTML = f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">SA3 Regions
      <span class="kpi-help" data-tooltip="SA3 regions matching the current filter selection">?</span>
    </div>
    <div class="kpi-value">{n_sa3}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">In Deficit
      <span class="kpi-help" data-tooltip="Regions where high-needs HCP demand exceeds residential beds (pressure &gt; 1.0)">?</span>
    </div>
    <div class="kpi-value">{n_deficit}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Median Quality Score
      <span class="kpi-help" data-tooltip="Mean of 4 ACQSC star-rating sub-dimensions">?</span>
    </div>
    <div class="kpi-value">{med_quality}<span class="kpi-suffix"> /5</span></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Median Care Gap Index
      <span class="kpi-help" data-tooltip="access_rate / quality_score — higher = more underserved">?</span>
    </div>
    <div class="kpi-value">{med_cgi}<span class="kpi-suffix"> /1</span></div>
  </div>
</div>"""

# ── Page routing ───────────────────────────────────────────────────────────────
if page == "home":
    pg_home.render(hero_b64, KPI_HTML)

elif page == "map":
    pg_map.render(df, gdf, year_sel)

elif page == "correlation":
    pg_corr.render(df, ratings, funding, year_sel)

elif page == "reveal":
    pg_reveal.render(df, year_sel, n_deficit)

elif page == "mandate":
    pg_mandate.render(ratings)

else:
    pg_home.render(hero_b64, KPI_HTML)
