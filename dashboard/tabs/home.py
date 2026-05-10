import streamlit as st
from tabs.utils import C


def render(hero_b64: str, KPI_HTML: str) -> None:
    hero_style = (
        f"background:linear-gradient(rgba(27,63,110,0.60),rgba(27,63,110,0.60)),"
        f"url('data:image/jpeg;base64,{hero_b64}') center/cover no-repeat;"
        if hero_b64
        else f"background:linear-gradient(135deg,{C['navy']},{C['teal']});"
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
        '<p class="data-caption">Data compiled from Aged Care Official Website &amp; ABS 2021–2026</p>',
        unsafe_allow_html=True,
    )
