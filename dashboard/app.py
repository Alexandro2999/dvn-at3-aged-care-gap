"""
Australia's Aged Care Gap — DVN AT3 Dashboard
Design system: blue-spectrum / teal / gold / cream / care-gap-red
Navigation: query-param routing (?page=home|map|correlation|reveal|mandate|fullmap)

Advanced features (per pitch S9):
    1. Context-aware filtering — sidebar State + MMM choices flow into every
       chapter; SA3 'current MMM' resolution preserves cross-year continuity.
       Implementation: this file, lines ~548–577.
    2. What-if slider — Chapter 4 staffing-minutes target. See tabs/ch4_mandate.py.
    3. Click-drill — Chapter 3 waitlist bar → HCP level donut. See tabs/ch3_reveal.py.
    4. Forecast scenario toggle — 2025 projection across Home/Ch1/fullmap with
       sidebar-driven Baseline / Aggressive aging / Stagnation scenarios.
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import base64
import os
import sys
import urllib.request

# ── Make tabs/ importable ──────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from tabs.utils import C, MMM_COLOURS, ORG_COLOURS, SNAP_YEAR, MANDATE
import tabs.home           as pg_home
import tabs.ch1_map        as pg_map
import tabs.ch2_correlation as pg_corr
import tabs.ch3_reveal     as pg_reveal
import tabs.ch4_mandate    as pg_mandate
import tabs.fullmap        as pg_fullmap


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Australia's Aged-Care Gap · DVN AT3",
    page_icon="🏥",
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


_GEOJSON_URL = (
    'https://raw.githubusercontent.com/Alexandro2999/dvn-at3-aged-care-gap'
    '/main/data/raw/abs_geography/sa3_simplified.geojson'
)

@st.cache_resource
def load_geojson():
    geojson = os.path.join(GEO, 'sa3_simplified.geojson')
    if not os.path.exists(geojson):
        try:
            os.makedirs(os.path.dirname(geojson), exist_ok=True)
            urllib.request.urlretrieve(_GEOJSON_URL, geojson)
        except Exception:
            return None
    gdf = gpd.read_file(geojson)
    gdf['sa3_code'] = pd.to_numeric(gdf['sa3_code'], errors='coerce').astype('Int64')
    gdf = gdf[gdf.geometry.notna()].reset_index(drop=True)
    return gdf


@st.cache_data
def load_supply():
    return pd.read_csv(os.path.join(CLEAN, 'service_supply_by_sa3.csv'))


@st.cache_data
def load_population():
    return pd.read_csv(os.path.join(CLEAN, 'abs_population_by_sa3.csv'))


@st.cache_data
def load_acpr_residential_users():
    return pd.read_csv(os.path.join(CLEAN, 'residential_users_by_acpr.csv'))


@st.cache_data
def load_acpr_homecare_users():
    return pd.read_csv(os.path.join(CLEAN, 'home_care_users_by_acpr.csv'))


@st.cache_data
def load_service_users():
    return pd.read_csv(os.path.join(CLEAN, 'service_users_by_sa3.csv'))


master        = load_master()
ratings       = load_ratings()
funding       = load_funding()
supply        = load_supply()
population    = load_population()
service_users = load_service_users()
acpr_res      = load_acpr_residential_users()
acpr_hc       = load_acpr_homecare_users()
gdf           = load_geojson()

hero_b64 = _b64(os.path.join(ASSETS, 'img-landing-bg.jpg'))
ico_b64  = _b64(os.path.join(ASSETS, 'ico-dashboard.png'))

# ── CSS ────────────────────────────────────────────────────────────────────────
NAV_H = 64
CSS = f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp, [class*="css"], button, input, select, textarea {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}}

#MainMenu, footer {{ visibility: hidden; }}
/* Keep header element + sidebar toggle visible ABOVE the custom nav-bar.
   pointer-events:none on header lets clicks pass through to nav-bar except
   on the actual buttons (which re-enable pointer events). */
header[data-testid="stHeader"] {{
    background: transparent !important;
    box-shadow: none !important;
    pointer-events: none !important;
    z-index: 10000 !important;
}}
header[data-testid="stHeader"] button {{
    pointer-events: auto !important;
    z-index: 10001 !important;
}}
header [data-testid="stMainMenu"],
.stDeployButton,
div[data-testid="stToolbar"] {{ display: none !important; }}

html, body {{ font-size: 18px !important; }}
/* Subtle paper-grain texture overlay on cream background — gives the page an editorial, printed-report feel without distracting from charts. */
.stApp, section[data-testid="stAppViewContainer"] {{
    background:
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.067 0 0 0 0 0.063 0 0 0 0 0.055 0 0 0 0.045 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>"),
        {C['bg']};
    background-blend-mode: multiply;
    font-size: 18px;
}}

.main .block-container {{
    padding-top: {NAV_H + 16}px !important;
    padding-bottom: 56px !important;
    max-width: 1380px;
}}

section[data-testid="stSidebar"] {{
    background: {C['white']} !important;
    border-right: 1px solid {C['border']};
}}
section[data-testid="stSidebar"] * {{ pointer-events: auto !important; }}
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

/* Force navy text on ALL expander summary descendants outside sidebar */
html body details[data-testid="stExpander"] summary,
html body details[data-testid="stExpander"] summary * {{
    color: {C['navy']} !important;
    font-weight: 600 !important;
}}
html body details[data-testid="stExpander"] summary svg,
html body details[data-testid="stExpander"] summary svg * {{
    fill: {C['navy']} !important;
}}
/* Sidebar expanders re-asserted white (later rule + matching specificity) */
html body section[data-testid="stSidebar"] details[data-testid="stExpander"] summary,
html body section[data-testid="stSidebar"] details[data-testid="stExpander"] summary * {{
    color: white !important;
}}
html body section[data-testid="stSidebar"] details[data-testid="stExpander"] summary svg,
html body section[data-testid="stSidebar"] details[data-testid="stExpander"] summary svg * {{
    fill: white !important;
}}

section[data-testid="stSidebar"] label {{ color: {C['navy']} !important; font-weight: 600 !important; }}
section[data-testid="stSidebar"] p {{ color: {C['navy']} !important; }}
section[data-testid="stSidebar"] span {{ color: {C['navy']} !important; }}
div[data-testid="stRadio"] label p {{ color: {C['navy']} !important; font-weight: 500 !important; }}
div[data-testid="stMultiSelect"] span[data-baseweb="tag"] span {{ color: white !important; }}

/* ── Main content — all widget labels and body text ── */
body [data-testid="stWidgetLabel"] p {{ color: {C['navy']} !important; font-weight: 600 !important; font-size: 20px !important; }}
body [data-testid="stWidgetLabel"] {{ color: {C['navy']} !important; font-size: 20px !important; }}
body .stSelectbox label, body .stRadio label, body .stTextInput label,
body .stSlider label, body .stCheckbox label, body .stNumberInput label {{
    color: {C['navy']} !important; font-weight: 600 !important; font-size: 20px !important;
}}
body div[role="radiogroup"] label p {{ color: {C['navy']} !important; font-weight: 500 !important; font-size: 20px !important; }}
body div[role="radiogroup"] label span {{ color: {C['navy']} !important; font-size: 20px !important; }}
body div[data-baseweb="select"] div {{ color: {C['navy']} !important; font-size: 20px !important; }}
div[data-baseweb="select"] > div {{
    background: {C['white']} !important;
    border-color: {C['border']} !important;
    border-radius: 8px !important;
}}
div[data-baseweb="select"] > div:hover {{
    border-color: {C['teal']} !important;
}}
body button[data-baseweb="tab"] p, body button[data-baseweb="tab"] span {{
    color: {C['navy']} !important; font-weight: 600 !important; font-size: 21px !important;
}}
body button[data-baseweb="tab"][aria-selected="true"] p,
body button[data-baseweb="tab"][aria-selected="true"] span {{
    color: {C['navy']} !important;
}}

.stPlotlyChart {{
    background: {C['white']}; border-radius: 12px;
    border: 1px solid {C['border']}; padding: 4px;
}}

body [data-testid="stAlert"] {{ opacity: 1 !important; }}
body [data-testid="stAlert"] p, body [data-testid="stAlert"] span,
body [data-testid="stAlert"] li, body [data-testid="stAlert"] strong,
body [data-testid="stAlert"] div {{
    color: {C['navy']} !important; font-size: 20px !important; line-height: 1.6 !important;
}}

body .stTextInput input {{
    border-radius: 24px !important; border: 1px solid {C['border']} !important;
    padding: 8px 20px !important; background: {C['white']} !important;
    font-size: 20px !important;
}}
body .stTextInput label {{ color: {C['navy']} !important; font-weight: 700 !important; font-size: 20px !important; }}

.stSlider [data-baseweb="slider"] [role="slider"] {{
    background-color: {C['teal']} !important; border-color: {C['teal']} !important;
}}
.stSlider [data-baseweb="track"] [data-testid="stSliderTrackFill"] {{
    background-color: {C['teal']} !important;
}}

body [data-testid="stMetric"] {{
    background: {C['white']}; border: 1px solid {C['border']};
    border-radius: 12px; padding: 16px 20px;
    min-height: 130px !important;
    display: flex !important; flex-direction: column !important; justify-content: space-between !important;
}}
body [data-testid="stMetricLabel"] {{ color: {C['navy']} !important; font-weight: 700 !important; font-size: 19px !important; }}
body [data-testid="stMetricValue"] {{ color: {C['navy']} !important; font-size: 35px !important; font-weight: 800 !important; }}
body [data-testid="stMetricDelta"] {{ font-size: 17px !important; }}

.nav-bar {{
    position: fixed; top: 0; left: calc(21rem - 16px); right: 0;
    height: {NAV_H}px; background: {C['navy']};
    display: flex; align-items: center; padding: 0 28px;
    z-index: 9999; box-shadow: 0 2px 12px rgba(0,0,0,0.18);
    border-radius: 0 0 10px 10px; margin: 0 10px 0 0;
}}
.nav-bar a {{ text-decoration: none !important; }}
.nav-home-btn {{
    color: rgba(255,255,255,0.6); padding: 6px 18px; border-radius: 6px;
    font-weight: 700; font-size: 20px; white-space: nowrap;
    cursor: pointer; transition: background 0.15s, color 0.15s; display: inline-block;
    background: rgba(255,255,255,0.12);
}}
.nav-home-btn:hover {{ background: rgba(255,255,255,0.22); color: white !important; }}
.nav-home-btn.active {{ background: {C['teal']}; color: white !important; }}

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
    display: block; color: rgba(255,255,255,0.55) !important; font-size: 20px;
    padding: 5px 14px; border-radius: 6px; white-space: nowrap; transition: all 0.15s;
}}
.nav-ch-link:hover {{ color: white !important; background: rgba(255,255,255,0.1); }}
.nav-ch.active .nav-ch-link {{ background: {C['teal']}; color: white !important; font-weight: 600; }}

.kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 0 0 8px; }}
.kpi-card {{
    background: {C['white']}; border: 1px solid {C['border']};
    border-radius: 12px; padding: 20px 24px 18px;
    box-shadow: 0 1px 3px rgba(17, 48, 78, 0.04);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}}
.kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(17, 48, 78, 0.10);
}}
/* Soft pop-in for KPI values + sparklines on initial render */
@keyframes kpiPop {{
    0%   {{ opacity: 0; transform: translateY(6px) scale(0.96); }}
    100% {{ opacity: 1; transform: translateY(0)   scale(1);    }}
}}
.kpi-value {{
    animation: kpiPop 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
}}
.kpi-card svg {{
    animation: kpiPop 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.1s both;
}}
.kpi-label {{
    color: {C['navy']}; font-weight: 700; font-size: 19px;
    letter-spacing: 0.06em; text-transform: uppercase;
    display: flex; align-items: center; gap: 6px; margin-bottom: 10px;
}}
.kpi-help {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 15px; height: 15px; background: {C['border']}; border-radius: 50%;
    font-size: 14px; color: {C['muted']}; font-weight: 700;
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

.sec-h1 {{ color: {C['navy']}; font-size: 33px; font-weight: 900; margin-bottom: 10px; line-height: 1.2; letter-spacing: -0.3px; }}
.sec-p {{ color: #3D4F63; font-size: 21px; margin-bottom: 20px; line-height: 1.6; max-width: 900px; }}
.sub-h {{ color: {C['navy']}; font-size: 23px; font-weight: 700; margin: 24px 0 8px; }}

/* Streamlit markdown headings — force navy + tighter spacing */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
    color: {C['navy']} !important;
    font-weight: 800 !important;
}}
.stMarkdown h3 {{ font-size: 24px !important; margin-top: 10px !important; margin-bottom: 8px !important; }}
.stMarkdown h4 {{ font-size: 20px !important; margin-top: 8px !important; margin-bottom: 6px !important; }}
.stMarkdown hr {{ margin: 10px 0 12px !important; border-color: {C['border']} !important; }}

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
    color: {C['navy']}; font-size: 20px;
}}

.whatif-box {{
    background: {C['light']}; border: 1px solid {C['border']};
    border-radius: 12px; padding: 20px 24px; margin: 28px 0 16px;
}}
.whatif-title {{ color: {C['navy']}; font-size: 1.1rem; font-weight: 700; margin-bottom: 4px; }}
.whatif-sub {{ color: {C['muted']}; font-size: 0.87rem; margin-bottom: 0; }}

.data-caption {{ color: {C['muted']}; font-size: 0.88rem; font-style: italic; margin-top: 28px; }}

span[data-baseweb="tag"] {{
    background-color: {C['navy']} !important; border-color: {C['navy']} !important;
    border-radius: 4px !important;
}}
span[data-baseweb="tag"] span {{ color: white !important; }}
span[data-baseweb="tag"] button span svg {{ fill: rgba(255,255,255,0.75) !important; }}

input[type="radio"] {{ accent-color: {C['navy']} !important; }}

li[role="option"] span[data-baseweb="checkbox"] > div {{ border-color: {C['teal']} !important; }}
li[role="option"][aria-selected="true"] span[data-baseweb="checkbox"] > div {{
    background-color: {C['teal']} !important; border-color: {C['teal']} !important;
}}
</style>"""

st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)
st.markdown(CSS, unsafe_allow_html=True)

# Clear any stale Streamlit sidebar-collapsed state from localStorage so the
# initial_sidebar_state="expanded" actually takes effect each load.
st.components.v1.html(
    """
    <script>
    (function() {
        try {
            var keys = Object.keys(window.parent.localStorage);
            keys.forEach(function(k) {
                if (k.toLowerCase().indexOf('sidebar') !== -1) {
                    window.parent.localStorage.removeItem(k);
                }
            });
        } catch (e) {}
        // If a collapsed-control button is present, click it to open sidebar
        setTimeout(function() {
            try {
                var doc = window.parent.document;
                var btn = doc.querySelector('[data-testid="stSidebarCollapsedControl"] button');
                if (btn) btn.click();
            } catch (e) {}
        }, 300);
    })();
    </script>
    """,
    height=0,
)

# ── Navigation bar ─────────────────────────────────────────────────────────────
page = st.query_params.get("page", "home")

NAV_CHAPTERS = [
    ("Chapter 1: The Gap",      "map"),
    ("Chapter 2: The Cause",    "correlation"),
    ("Chapter 3: The Victims",  "reveal"),
    ("Chapter 4: The Verdict",  "mandate"),
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
            f'<a href="?page=home" target="_self" aria-label="Return to dashboard home"'
            f' style="display:inline-block;margin-bottom:12px">'
            f'<img src="data:image/png;base64,{ico_b64}" width="52"'
            f' alt="Australia\'s Aged Care Gap dashboard logo"'
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
        f'<p style="margin:0 0 14px;color:{C["navy"]};font-size:0.78rem">'
        f'State &amp; remoteness — apply to all tabs</p>',
        unsafe_allow_html=True,
    )

    with st.expander("State / Territory", expanded=True):
        states = sorted(master['state'].dropna().unique())
        state_sel = st.multiselect("State", states, default=states,
                                   label_visibility="collapsed")

    with st.expander("Remoteness (MMM)"):
        st.caption(
            "**MMM = Modified Monash Model** — ABS rural/urban classifier. "
            "MM1 = Major city · MM4 = Remote · MM7 = Very remote."
        )
        mmm_opts = sorted(master['mmm_code'].dropna().unique())
        mmm_sel = st.multiselect("MMM", mmm_opts, default=mmm_opts,
                                 label_visibility="collapsed")

# ── Filter slices ──────────────────────────────────────────────────────────────
_states = state_sel if state_sel else states
_mmm    = mmm_sel   if mmm_sel   else mmm_opts

# SA3-level "current" mmm_code (latest year) — used for filtering so that an SA3
# whose mmm_code drifted across years is treated by its most-recent classification.
# Keeps ALL years of an SA3 together if its latest mmm matches the filter.
_sa3_current_mmm = (
    master.dropna(subset=['mmm_code'])
    .sort_values('year')
    .drop_duplicates('sa3_code', keep='last')
    [['sa3_code', 'mmm_code']]
    .rename(columns={'mmm_code': '_current_mmm'})
)
master_filt = (
    master.merge(_sa3_current_mmm, on='sa3_code', how='left')
)
master_filt = master_filt[
    (master_filt['state'].isin(_states)) &
    (master_filt['_current_mmm'].isin(_mmm))
].drop(columns='_current_mmm').copy()

# Whether the sidebar filter is narrower than the full master universe.
# Used by tabs whose hero metric should remain the national figure when the
# user has not actively narrowed the scope.
filter_active = (set(_states) != set(states)) or (set(_mmm) != set(mmm_opts))

# Latest-year slice (used by reveal tab's n_deficit count)
_latest = master_filt[master_filt['year'] == master_filt['year'].max()]
n_deficit = int((_latest.drop_duplicates('sa3_name')['waitlist_pressure'] > 1.0).sum()) if not _latest.empty else 0

# ── Page routing ───────────────────────────────────────────────────────────────
if page == "home":
    pg_home.render(hero_b64, master_filt, gdf, supply, population, ratings, service_users)

elif page == "fullmap":
    pg_fullmap.render(master_filt, gdf, supply, population, service_users=service_users, ratings=ratings)

elif page == "map":
    pg_map.render(master_filt, gdf, supply, population, ratings, service_users)

elif page == "correlation":
    pg_corr.render(master_filt, ratings, funding, supply)

elif page == "reveal":
    pg_reveal.render(master_filt, supply, n_deficit, service_users, filter_active=filter_active)

elif page == "mandate":
    pg_mandate.render(ratings, master_filt, filter_active=filter_active)

else:
    pg_home.render(hero_b64, master_filt, gdf, supply, population, ratings, service_users)
