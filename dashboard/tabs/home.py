import streamlit as st
from tabs.utils import C


AUDIENCE_CARDS_HTML = f"""
<div style="margin: 32px 0 16px; text-align:center;
            color:{C['navy']}; font-weight:700; font-size:1.1rem;">
    Pick your story
</div>
<div style="display:grid; grid-template-columns: repeat(3, 1fr);
            gap: 18px; margin-bottom: 28px;">

  <a href="?page=map" target="_self" style="text-decoration:none;">
    <div style="background:{C['white']}; border:1.5px solid {C['border']};
                border-radius: 14px; padding: 22px 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                transition: transform 0.15s, box-shadow 0.15s;
                cursor: pointer; min-height: 170px;">
      <div style="font-size:1.6rem; margin-bottom:6px;">👨‍👩‍👧</div>
      <div style="color:{C['navy']}; font-weight:800;
                  font-size:1.0rem; margin-bottom:6px;">Families</div>
      <div style="color:{C['muted']}; font-size:0.82rem; line-height:1.45;">
        Is care near my family any good?<br>
        Find your area on the map.
      </div>
      <div style="color:{C['teal']}; font-weight:700; font-size:0.8rem;
                  margin-top:14px;">→ Chapter 1: The Map</div>
    </div>
  </a>

  <a href="?page=forecast" target="_self" style="text-decoration:none;">
    <div style="background:{C['white']}; border:1.5px solid {C['border']};
                border-radius: 14px; padding: 22px 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                cursor: pointer; min-height: 170px;">
      <div style="font-size:1.6rem; margin-bottom:6px;">💼</div>
      <div style="color:{C['navy']}; font-weight:800;
                  font-size:1.0rem; margin-bottom:6px;">Workers</div>
      <div style="color:{C['muted']}; font-size:0.82rem; line-height:1.45;">
        Where are workers most needed?<br>
        See where supply is collapsing.
      </div>
      <div style="color:{C['teal']}; font-weight:700; font-size:0.8rem;
                  margin-top:14px;">→ Chapter 5: The Forecast</div>
    </div>
  </a>

  <a href="?page=correlation" target="_self" style="text-decoration:none;">
    <div style="background:{C['white']}; border:1.5px solid {C['border']};
                border-radius: 14px; padding: 22px 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                cursor: pointer; min-height: 170px;">
      <div style="font-size:1.6rem; margin-bottom:6px;">📊</div>
      <div style="color:{C['navy']}; font-weight:800;
                  font-size:1.0rem; margin-bottom:6px;">Investors</div>
      <div style="color:{C['muted']}; font-size:0.82rem; line-height:1.45;">
        Where are the market gaps?<br>
        See ownership &amp; funding patterns.
      </div>
      <div style="color:{C['teal']}; font-weight:700; font-size:0.8rem;
                  margin-top:14px;">→ Chapter 2: The Why</div>
    </div>
  </a>

</div>
"""


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
        f'<a class="hero-btn" href="?page=map" target="_self">▶ Start the detective arc</a>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(KPI_HTML, unsafe_allow_html=True)
    st.markdown(AUDIENCE_CARDS_HTML, unsafe_allow_html=True)
    st.markdown(
        '<p class="data-caption">Data compiled from Aged Care Official Website &amp; ABS 2021–2026</p>',
        unsafe_allow_html=True,
    )
