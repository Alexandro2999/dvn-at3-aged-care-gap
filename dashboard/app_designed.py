"""
Australia's Aged Care Gap — DVN AT3 Dashboard Redesign
Design system: blue-spectrum / teal / gold / cream / care-gap-red
Navigation: query-param routing (?page=home|map|correlation|reveal|mandate)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import base64
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Australia's Aged Care Gap",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.abspath(__file__))
CLEAN  = os.path.join(BASE, '..', 'data', 'clean')
GEO    = os.path.join(BASE, '..', 'data', 'raw', 'abs_geography')
# Prefer dashboard-local assets copy; fall back to source
_assets_local = os.path.join(BASE, 'assets')
_assets_src   = os.path.join(BASE, '..', 'notebooks', 'artist', 'assets')
ASSETS = _assets_local if os.path.isdir(_assets_local) else _assets_src

# ── Design tokens ─────────────────────────────────────────────────────────────
C = dict(
    navy   = '#1B3F6E',
    teal   = '#00A79D',
    gold   = '#F5C842',
    cream  = '#FDF4D0',
    red    = '#D94F3D',
    bg     = '#E3F1FA',
    white  = '#FFFFFF',
    muted  = '#6B7C93',
    border = '#C8DCF0',
    light  = '#F3F9FE',
)

MMM_COLOURS = {
    'MM1': '#1B3F6E', 'MM2': '#2E5FA3', 'MM3': '#4A7FC1',
    'MM4': '#6B9ED4', 'MM5': '#8FBCE3', 'MM6': '#00A79D', 'MM7': '#7ECDC8',
}

ORG_COLOURS = {
    'profit':         '#D94F3D',
    'not_for_profit': '#1B3F6E',
    'government':     '#00A79D',
}

SNAP_YEAR = {
    'May 2023': 2023, 'August 2023': 2023, 'December 2023': 2023,
    'February 2024': 2024, 'May 2024': 2024, 'July 2024': 2024, 'November 2024': 2024,
    'February 2025': 2025, 'May 2025': 2025, 'August 2025': 2025, 'October 2025': 2025,
    'February 2026': 2026,
}
MANDATE = pd.Timestamp('2023-10-01')

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data
def _b64(path: str) -> str:
    if not os.path.exists(path):
        return ''
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()


def theme(fig, height: int | None = None):
    """Apply consistent Plotly chart theme."""
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter,-apple-system,BlinkMacSystemFont,sans-serif', color=C['navy'], size=12),
        title_font=dict(size=13, color=C['navy']),
        margin=dict(l=0, r=8, t=48, b=0),
        legend=dict(
            bgcolor='rgba(255,255,255,0.92)',
            bordercolor=C['border'],
            borderwidth=1,
        ),
        xaxis=dict(gridcolor=C['bg'], linecolor=C['border'], tickcolor=C['border']),
        yaxis=dict(gridcolor=C['bg'], linecolor=C['border'], tickcolor=C['border']),
    )
    if height:
        fig.update_layout(height=height)
    return fig

# ── Data loading (cached, mutations inside load functions) ────────────────────
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
    df['org_type'] = df['Purpose'].str.strip().str.lower().map({
        'for profit': 'profit',
        'not for profit': 'not_for_profit',
        'government': 'government',
    }).fillna('unknown')
    df['period'] = df['snapshot_date'].apply(
        lambda d: 'After mandate' if d >= MANDATE else 'Before mandate'
    )
    return df


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
    return gdf.to_crs(epsg=4326)


master  = load_master()
ratings = load_ratings()
funding = load_funding()
gdf     = load_shapefile()

hero_b64 = _b64(os.path.join(ASSETS, 'img-landing-bg.jpg'))
ico_b64  = _b64(os.path.join(ASSETS, 'ico-dashboard.png'))

# ── CSS ───────────────────────────────────────────────────────────────────────
NAV_H = 64

CSS = f"""<style>
/* ── Reset Streamlit chrome ─────────────────────────────────────────────── */
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ display: none !important; }}
.stDeployButton, div[data-testid="stToolbar"] {{ display: none !important; }}

/* ── Page background ─────────────────────────────────────────────────────── */
.stApp,
section[data-testid="stAppViewContainer"] {{
    background: {C['bg']};
}}

/* ── Main content — reserve space for fixed nav ──────────────────────────── */
.main .block-container {{
    padding-top: {NAV_H + 16}px !important;
    padding-bottom: 56px !important;
    max-width: 1380px;
}}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: {C['white']} !important;
    border-right: 1px solid {C['border']};
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1.5rem !important;
}}

/* ── Sidebar expander accordion ──────────────────────────────────────────── */
section[data-testid="stSidebar"] details[data-testid="stExpander"] {{
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid {C['border']} !important;
    border-radius: 0 !important;
    margin: 0 0 6px !important;
}}
section[data-testid="stSidebar"] details[data-testid="stExpander"] summary {{
    background: {C['navy']} !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 10px 14px !important;
}}
section[data-testid="stSidebar"] details[data-testid="stExpander"][open] summary {{
    border-radius: 8px 8px 0 0 !important;
}}
section[data-testid="stSidebar"] details[data-testid="stExpander"] > div[data-testid="stExpanderDetails"] {{
    background: {C['light']} !important;
    border: 1px solid {C['border']};
    border-top: none;
    border-radius: 0 0 8px 8px;
    padding: 12px 10px !important;
}}
/* Hide expander chevron arrow colour override */
section[data-testid="stSidebar"] details summary svg {{
    fill: white !important;
}}

/* ── Plotly containers ───────────────────────────────────────────────────── */
.stPlotlyChart {{
    background: {C['white']};
    border-radius: 12px;
    border: 1px solid {C['border']};
    padding: 4px;
}}

/* ── Text input ──────────────────────────────────────────────────────────── */
.stTextInput input {{
    border-radius: 24px !important;
    border: 1px solid {C['border']} !important;
    padding: 8px 20px !important;
    background: {C['white']} !important;
}}
.stTextInput label {{
    color: {C['navy']} !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}}

/* ── Slider ──────────────────────────────────────────────────────────────── */
.stSlider [data-baseweb="slider"] [role="slider"] {{
    background-color: {C['teal']} !important;
    border-color: {C['teal']} !important;
}}
.stSlider [data-baseweb="track"] [data-testid="stSliderTrackFill"] {{
    background-color: {C['teal']} !important;
}}

/* ── st.metric cards ─────────────────────────────────────────────────────── */
[data-testid="stMetric"] {{
    background: {C['white']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 16px 20px;
}}
[data-testid="stMetricLabel"] {{ color: {C['teal']} !important; font-weight: 700 !important; }}
[data-testid="stMetricValue"] {{ color: {C['navy']} !important; }}

/* ── Fixed nav bar — starts after the sidebar, never overlaps it ─────────── */
.nav-bar {{
    position: fixed;
    top: 0;
    /* Sidebar is ~21rem; pull left 16px for visual balance */
    left: calc(21rem - 16px);
    right: 0;
    height: {NAV_H}px;
    background: {C['navy']};
    display: flex;
    align-items: center;
    padding: 0 28px;
    z-index: 9999;
    box-shadow: 0 2px 12px rgba(0,0,0,0.18);
    border-radius: 0 0 10px 10px;
    margin: 0 10px 0 0;
}}
.nav-bar a {{ text-decoration: none !important; }}
.nav-home-btn {{
    color: white;
    padding: 6px 18px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 14px;
    white-space: nowrap;
    cursor: pointer;
    transition: background 0.15s;
    display: inline-block;
}}
.nav-home-btn:hover {{ background: {C['teal']}; color: white !important; }}
.nav-home-btn.active {{ background: {C['teal']}; color: white !important; }}

.nav-chapters {{
    display: flex;
    align-items: flex-end;
    margin-left: auto;
    position: relative;
    padding-top: 18px;
    gap: 0;
}}
/* Progress line connecting the dots */
.nav-chapters::before {{
    content: '';
    position: absolute;
    top: 7px; left: 24px; right: 24px;
    height: 2px;
    background: rgba(255,255,255,0.85);
    pointer-events: none;
}}
.nav-ch {{
    position: relative;
    padding: 0 4px;
}}
/* Progress dot */
.nav-ch::before {{
    content: '';
    position: absolute;
    top: -14px;
    left: 50%;
    transform: translateX(-50%);
    width: 8px; height: 8px;
    border-radius: 50%;
    background: rgba(255,255,255,0.85);
    z-index: 1;
}}
.nav-ch.active::before {{
    background: {C['teal']};
    box-shadow: 0 0 0 3px rgba(0,167,157,0.3);
}}
.nav-ch-link {{
    display: block;
    color: white !important;
    font-size: 13px;
    padding: 5px 14px;
    border-radius: 6px;
    white-space: nowrap;
    transition: all 0.15s;
}}
.nav-ch-link:hover {{
    color: white !important;
    background: rgba(255,255,255,0.1);
}}
.nav-ch.active .nav-ch-link {{
    background: {C['teal']};
    color: white !important;
    font-weight: 600;
}}

/* ── KPI card grid ───────────────────────────────────────────────────────── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 0 0 8px;
}}
.kpi-card {{
    background: {C['white']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 20px 24px 18px;
}}
.kpi-label {{
    color: {C['teal']};
    font-weight: 700;
    font-size: 0.78rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 10px;
}}
.kpi-help {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 15px; height: 15px;
    background: {C['border']};
    border-radius: 50%;
    font-size: 9px;
    color: {C['muted']};
    font-weight: 700;
    position: relative;
    cursor: help;
}}
/* Tooltip bubble */
.kpi-help::after {{
    content: attr(data-tooltip);
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    background: {C['navy']};
    color: white;
    padding: 7px 13px;
    border-radius: 8px;
    font-size: 0.76rem;
    font-weight: 400;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.18s;
    z-index: 99999;
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
}}
/* Arrow */
.kpi-help::before {{
    content: '';
    position: absolute;
    bottom: calc(100% + 2px);
    left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: {C['navy']};
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.18s;
    z-index: 99999;
}}
.kpi-help:hover::after,
.kpi-help:hover::before {{
    opacity: 1;
}}
.kpi-value {{
    color: {C['navy']};
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1;
}}
.kpi-suffix {{
    font-size: 1rem;
    color: {C['muted']};
    font-weight: 500;
}}

/* ── Page typography ─────────────────────────────────────────────────────── */
.sec-h1 {{
    color: {C['navy']};
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 10px;
    line-height: 1.2;
}}
.sec-p {{
    color: {C['muted']};
    font-size: 0.95rem;
    margin-bottom: 20px;
    line-height: 1.65;
    max-width: 900px;
}}
.sub-h {{
    color: {C['navy']};
    font-size: 1.05rem;
    font-weight: 700;
    margin: 24px 0 8px;
}}

/* ── Hero section ────────────────────────────────────────────────────────── */
.hero-wrap {{
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 28px;
    min-height: 480px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}}
.hero-inner {{
    text-align: center;
    color: white;
    padding: 64px 48px;
    position: relative;
    z-index: 1;
}}
.hero-h {{
    font-size: 2.55rem;
    font-weight: 800;
    line-height: 1.25;
    margin-bottom: 32px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.3);
}}
.hero-btn {{
    display: inline-block;
    background: {C['teal']};
    color: white !important;
    text-decoration: none !important;
    padding: 16px 48px;
    border-radius: 40px;
    font-size: 1.1rem;
    font-weight: 700;
    transition: background 0.2s, transform 0.1s;
    box-shadow: 0 4px 16px rgba(0,167,157,0.35);
}}
.hero-btn:hover {{
    background: #007A72;
    transform: translateY(-1px);
}}

/* ── Neighbourhood match card ────────────────────────────────────────────── */
.nb-card {{
    background: {C['white']};
    border: 1.5px solid {C['teal']};
    border-radius: 10px;
    padding: 14px 20px;
    margin-bottom: 16px;
    color: {C['navy']};
    font-size: 0.95rem;
}}

/* ── What-IF section box ─────────────────────────────────────────────────── */
.whatif-box {{
    background: {C['light']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 20px 24px;
    margin: 28px 0 16px;
}}
.whatif-title {{
    color: {C['navy']};
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 4px;
}}
.whatif-sub {{
    color: {C['muted']};
    font-size: 0.87rem;
    margin-bottom: 0;
}}

/* ── Data caption ────────────────────────────────────────────────────────── */
.data-caption {{
    color: {C['muted']};
    font-size: 0.8rem;
    font-style: italic;
    margin-top: 28px;
}}

/* ── Multiselect tags (state pills: ACT, NSW … and MMM: MM1 …) ───────────── */
span[data-baseweb="tag"] {{
    background-color: {C['navy']} !important;
    border-color: {C['navy']} !important;
    border-radius: 4px !important;
}}
span[data-baseweb="tag"] span {{
    color: white !important;
}}
span[data-baseweb="tag"] button span svg {{
    fill: rgba(255,255,255,0.75) !important;
}}

/* ── Radio button selected state ─────────────────────────────────────────── */
div[data-baseweb="radio"] div[role="radio"][aria-checked="true"]  {{
    background-color: {C['teal']} !important;
    border-color: {C['teal']} !important;
}}
/* Inner dot */
div[data-baseweb="radio"] div[role="radio"][aria-checked="true"] > div {{
    background-color: white !important;
}}
/* Hover ring */
div[data-baseweb="radio"]:hover div[role="radio"] {{
    border-color: {C['teal']} !important;
}}

/* ── Multiselect dropdown checkboxes ─────────────────────────────────────── */
li[role="option"] span[data-baseweb="checkbox"] > div {{
    border-color: {C['teal']} !important;
}}
li[role="option"][aria-selected="true"] span[data-baseweb="checkbox"] > div {{
    background-color: {C['teal']} !important;
    border-color: {C['teal']} !important;
}}
</style>"""

st.markdown(CSS, unsafe_allow_html=True)

# ── Navigation bar (sticky, content area only) ───────────────────────────────
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

# ── Sidebar ───────────────────────────────────────────────────────────────────
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
        year_sel = st.radio(
            "Year", [2023, 2024], index=1,
            horizontal=True,
            label_visibility="collapsed",
        )

    with st.expander("State / Territory"):
        states = sorted(master['state'].dropna().unique())
        state_sel = st.multiselect(
            "State", states, default=states,
            label_visibility="collapsed",
        )

    with st.expander("Remoteness (MMM)"):
        mmm_opts = sorted(master['mmm_code'].dropna().unique())
        mmm_sel = st.multiselect(
            "MMM", mmm_opts, default=mmm_opts,
            label_visibility="collapsed",
        )

# ── Filter master by sidebar ──────────────────────────────────────────────────
_state_filter = state_sel if state_sel else states
_mmm_filter   = mmm_sel if mmm_sel else mmm_opts

df = master[
    (master['year'] == year_sel) &
    (master['state'].isin(_state_filter)) &
    (master['mmm_code'].isin(_mmm_filter))
].copy()

# ── KPI values (computed once, shared across pages) ───────────────────────────
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
      <span class="kpi-help" data-tooltip="Mean of 4 ACQSC star-rating sub-dimensions (residents exp, staffing, compliance, quality measures)">?</span>
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

# ═══════════════════════════════════════════════════════════════════════════════
# HOME — Landing page
# ═══════════════════════════════════════════════════════════════════════════════
if page == "home":
    hero_style = (
        f"background:linear-gradient(rgba(27,63,110,0.60),rgba(27,63,110,0.60)),"
        f"url('data:image/jpeg;base64,{hero_b64}') center/cover no-repeat;"
        if hero_b64 else
        f"background:linear-gradient(135deg,{C['navy']},{C['teal']});"
    )
    st.markdown(
        f'<div class="hero-wrap" style="{hero_style}">'
        f'<div class="hero-inner">'
        f'<div class="hero-h">Which regions have the worst<br>'
        f'gap between quality and access,<br>and why?</div>'
        f'<a class="hero-btn" href="?page=map" target="_self">Discover the Map</a>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(KPI_HTML, unsafe_allow_html=True)
    st.markdown(
        f'<p class="data-caption">'
        f'Data compiled from Aged Care Official Website &amp; ABS 2021–2026</p>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# CHAPTER 1 — THE MAP
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "map":
    st.markdown('<div class="sec-h1">Is aged care near me any good?</div>', unsafe_allow_html=True)

    # Neighbourhood search (ADVANCED FEATURE 2 — visual tooltip on match)
    search = st.text_input(
        "Check my neighbourhood",
        placeholder="Type your area name (SA3)",
    )
    if search and not df.empty:
        try:
            from rapidfuzz import process as fz
            names = df['sa3_name'].dropna().unique().tolist()
            result = fz.extractOne(search, names)
            if result and result[1] >= 60:
                match_name = result[0]
                row = df[df['sa3_name'] == match_name].iloc[0]
                st.markdown(
                    f'<div class="nb-card">'
                    f'<b>{match_name}</b> ({row.get("state","")})'
                    f'&nbsp;&nbsp;·&nbsp;&nbsp;'
                    f'Care Gap Index: <b>{row["care_gap_index"]:.2f}</b>'
                    f'&nbsp;&nbsp;·&nbsp;&nbsp;'
                    f'Quality Score: <b>{row["quality_score"]:.2f}</b>'
                    f'&nbsp;&nbsp;·&nbsp;&nbsp;'
                    f'Access Rate: <b>{row["access_rate"]:.1f}%</b>'
                    f'&nbsp;&nbsp;·&nbsp;&nbsp;'
                    f'Remoteness: <b>{row.get("mmm_code","")}</b>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        except Exception:
            pass

    st.markdown(
        '<p class="sec-p">Each SA3 is coloured by <b>care_gap_index</b> — the ratio of access rate to quality score. '
        'Darker = more underserved. Two patterns emerge: high-access/low-quality metro areas '
        'and low-access/high-quality remote areas.</p>',
        unsafe_allow_html=True,
    )

    if gdf is not None and not df.empty:
        merged = gdf.merge(
            df[['sa3_code', 'sa3_name', 'state', 'mmm_code', 'care_gap_index',
                'quality_score', 'access_rate', 'waitlist_pressure', 'pop_65_plus']],
            on='sa3_code', how='left',
        )
        cgi_max = float(df['care_gap_index'].quantile(0.95))
        fig_map = px.choropleth(
            merged,
            geojson=merged.__geo_interface__,
            locations=merged.index,
            color='care_gap_index',
            color_continuous_scale=[[0, '#E3F1FA'], [0.4, '#4A7FC1'], [1, '#1B3F6E']],
            range_color=[0, cgi_max if cgi_max > 0 else 5],
            hover_data={
                'sa3_name': True, 'state': True, 'mmm_code': True,
                'care_gap_index': ':.2f', 'quality_score': ':.2f',
                'access_rate': ':.1f', 'pop_65_plus': ':,.0f',
            },
            title=f'Care Gap Index by SA3 ({year_sel}) — darker = more underserved',
            labels={'care_gap_index': 'Care Gap Index'},
        )
        fig_map.update_geos(fitbounds='locations', visible=False)
        fig_map.update_coloraxes(colorbar_title_text='Care Gap Index')
        theme(fig_map, height=520)
        st.plotly_chart(fig_map, use_container_width=True)
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

    # Top / Bottom 10 bar charts (replaces tables)
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            bot10 = df.nsmallest(10, 'access_rate')[['sa3_name', 'state', 'access_rate']].copy()
            bot10['label'] = bot10['sa3_name'] + ' (' + bot10['state'] + ')'
            fig_bot = px.bar(
                bot10.sort_values('access_rate'),
                x='access_rate', y='label',
                orientation='h',
                color_discrete_sequence=[C['teal']],
                text='access_rate',
                title=f'10 Most Underserved SA3s<br><sup>lowest access rate, {year_sel}</sup>',
                labels={'access_rate': 'Access Rate (% of 65+ in residential care)', 'label': ''},
            )
            fig_bot.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            theme(fig_bot, height=380)
            st.plotly_chart(fig_bot, use_container_width=True)

        with c2:
            top10 = df.nlargest(10, 'access_rate')[['sa3_name', 'state', 'access_rate']].copy()
            top10['label'] = top10['sa3_name'] + ' (' + top10['state'] + ')'
            fig_top = px.bar(
                top10.sort_values('access_rate'),
                x='access_rate', y='label',
                orientation='h',
                color_discrete_sequence=[C['teal']],
                text='access_rate',
                title=f'10 Best Served SA3s<br><sup>highest access rate, {year_sel}</sup>',
                labels={'access_rate': 'Access Rate (% of 65+ in residential care)', 'label': ''},
            )
            fig_top.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            theme(fig_top, height=380)
            st.plotly_chart(fig_top, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CHAPTER 2 — THE CORRELATION
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "correlation":
    st.markdown('<div class="sec-h1">Who runs the best facilities?</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sec-p">Quality differences are not explained by geography — they are explained by <b>ownership</b>. '
        'Government facilities average 4.21 vs for-profit 3.68 (gap = 0.53 pts). '
        'Remote areas score higher <i>because</i> they have fewer for-profit providers.</p>',
        unsafe_allow_html=True,
    )

    latest = ratings[ratings['snapshot_date'] == ratings['snapshot_date'].max()]
    latest = latest[latest['org_type'] != 'unknown']

    # 1) Quality by org type — full width
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
        x='mean', y='label',
        orientation='h',
        color='org_type',
        color_discrete_map={k: ORG_COLOURS.get(k, C['teal']) for k in org_q['org_type']},
        text='annotation',
        title='Average Quality Score by Ownership Type<br><sup>February 2026 snapshot</sup>',
        labels={'mean': 'Avg Quality Score (1–5)', 'label': ''},
    )
    fig_org.add_vline(
        x=nat_avg, line_dash='dot', line_color=C['teal'],
        annotation_text=f'National avg {nat_avg:.2f}',
        annotation_position='top right',
    )
    fig_org.update_traces(textposition='outside', textfont_size=11)
    fig_org.update_layout(showlegend=False, xaxis_range=[0, 5])
    theme(fig_org, height=260)
    st.plotly_chart(fig_org, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        # Box plot: quality score by remoteness
        fig_box = px.box(
            latest[latest['mmm_code'].notna()],
            x='mmm_code', y='quality_score',
            color='mmm_code',
            color_discrete_map=MMM_COLOURS,
            title='Quality Score by Remoteness (MMM)<br><sup>February 2026 snapshot</sup>',
            labels={'quality_score': 'Quality Score (1–5)', 'mmm_code': 'Remoteness'},
            category_orders={'mmm_code': ['MM1', 'MM2', 'MM3', 'MM4', 'MM5', 'MM6', 'MM7']},
        )
        nat_med = latest['quality_score'].median()
        fig_box.add_hline(
            y=nat_med, line_dash='dot', line_color=C['teal'],
            annotation_text=f'National median {nat_med:.2f}',
            annotation_position='top right',
        )
        fig_box.update_layout(showlegend=False)
        theme(fig_box, height=360)
        st.plotly_chart(fig_box, use_container_width=True)

    with c2:
        # Government funding by org type
        fund_trend = (
            funding[funding['funding'] > 0]
            .groupby(['year', 'org_type'])['funding']
            .sum()
            .reset_index()
        )
        fund_trend['funding_b'] = fund_trend['funding'] / 1e9
        fig_fund = px.bar(
            fund_trend, x='year', y='funding_b', color='org_type',
            color_discrete_map=ORG_COLOURS,
            barmode='stack',
            title='Govt Funding by Ownership Type<br><sup>$B, 2019–2025</sup>',
            labels={'funding_b': 'Funding ($B)', 'org_type': 'Org type'},
        )
        fig_fund.update_layout(
            xaxis=dict(tickmode='linear', tick0=2019, dtick=1),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )
        theme(fig_fund, height=360)
        st.plotly_chart(fig_fund, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CHAPTER 3 — THE REVEAL
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "reveal":
    st.markdown('<div class="sec-h1">Which communities are being left behind?</div>', unsafe_allow_html=True)

    if df.empty:
        st.warning("No data for the current filter selection.")
    else:
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

        # Top 20 waitlist pressure — red = top quartile
        top20 = (
            df.nlargest(30, 'waitlist_pressure')
            .drop_duplicates('sa3_name')
            .head(20)
            .sort_values('waitlist_pressure')
        )
        q75 = top20['waitlist_pressure'].quantile(0.75)
        top20 = top20.copy()
        top20['colour'] = top20['waitlist_pressure'].apply(
            lambda x: C['red'] if x >= q75 else C['navy']
        )
        top20['row_label'] = top20['sa3_name'] + ' (' + top20['state'] + ')'

        fig_wp = px.bar(
            top20,
            x='waitlist_pressure', y='row_label',
            orientation='h',
            color='colour',
            color_discrete_map='identity',
            text='waitlist_pressure',
            hover_data={
                'state': True,
                'hcp_high_needs': ':,d',
                'residential_places': ':,d',
                'waitlist_pressure': ':.3f',
            },
            title=f'Top 20 SA3 Regions by Waitlist Pressure ({year_sel})<br>'
                  '<sup>Red = top quartile (highest pressure)</sup>',
            labels={'waitlist_pressure': 'Waitlist Pressure Index', 'row_label': ''},
        )
        fig_wp.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig_wp.add_vline(
            x=1.0, line_dash='dash', line_color=C['red'], line_width=1.5,
            annotation_text='Demand = Supply', annotation_position='top right',
        )
        fig_wp.update_layout(showlegend=False)
        theme(fig_wp, height=520)
        st.plotly_chart(fig_wp, use_container_width=True)

        # HCP level composition
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
                'L1 — Basic':                        '#A6C8FF',
                'L2 — Moderate':                     '#4589FF',
                'L3 — High (near-residential)':      C['gold'],
                'L4 — Very High (should be residential)': C['red'],
            },
            barmode='stack',
            title=f'HCP Level Composition by SA3: Who Is Actually Waiting? ({year_sel})<br>'
                  '<sup>Top 25 SA3s by total home care users</sup>',
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
            f'<div class="whatif-box">'
            f'<div class="whatif-title">What-IF Scenario</div>'
            f'<p class="whatif-sub">If all SA3s reached this beds_per_1k target, '
            f'how many exit the red zone?</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        whatif_target = st.slider(
            "Target beds per 1,000 elderly",
            min_value=30.0, max_value=80.0, value=50.0, step=1.0,
            label_visibility="collapsed",
        )
        n_below = int((df['beds_per_1k'] < whatif_target).sum())
        n_above = int(len(df) - n_below)
        nat_avg_beds = float(
            df['residential_places'].sum() / df['pop_65_plus'].sum() * 1000
        ) if df['pop_65_plus'].sum() > 0 else 0.0

        m1, m2, m3 = st.columns(3)
        m1.metric(
            "Current SA3s below target", f"{n_below}",
            help=f"SA3s below {whatif_target:.0f} beds per 1,000 elderly",
        )
        m2.metric("Current SA3s above target", f"{n_above}")
        m3.metric("National avg beds/1k", f"{nat_avg_beds:.1f}")

        med_beds = df['beds_per_1k'].median()
        fig_wi = px.histogram(
            df, x='beds_per_1k', nbins=30,
            color_discrete_sequence=[C['teal']],
            title=f'Distribution of beds per 1,000 elderly — target at {whatif_target:.0f}',
            labels={'beds_per_1k': 'Beds per 1,000 Elderly (65+)'},
        )
        fig_wi.add_vline(
            x=whatif_target, line_dash='dash', line_color=C['red'],
            annotation_text=f'Target: {whatif_target:.0f} beds per 1,000',
            annotation_position='top right',
        )
        fig_wi.add_vline(
            x=med_beds, line_dash='dot', line_color=C['muted'],
            annotation_text=f'Median: {med_beds:.1f}',
            annotation_position='top left',
        )
        theme(fig_wi, height=300)
        st.plotly_chart(fig_wi, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CHAPTER 4 — MANDATE EFFECT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "mandate":
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

    # National quality time series
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
            .mean()
            .reset_index()
        )
        fig_org_t = px.line(
            org_time, x='snapshot_date', y='quality_score',
            color='org_type',
            color_discrete_map=ORG_COLOURS,
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

    # Compliance trend (post-mandate)
    comp_time = (
        ratings[ratings['snapshot_date'] >= MANDATE]
        .dropna(subset=['fully_compliant'])
        .groupby('snapshot_date')['fully_compliant']
        .mean()
        .reset_index()
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
