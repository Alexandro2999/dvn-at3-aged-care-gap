"""Shared constants, colour maps, and Plotly theme for the DVN AT3 dashboard."""

import pandas as pd

C = dict(
    # Synced with slides_deck/Australias-Aged-Care-Gap.pptx — warmer editorial palette
    navy   = '#11304E',   # deeper than legacy '#1B3F6E'
    teal   = '#2BA39B',   # softer than legacy '#00A79D'
    gold   = '#D9A53B',   # warmer ochre than legacy '#F5C842'
    cream  = '#FAF6EC',   # warm cream from PPT bg
    red    = '#C44A38',   # darkened for WCAG AA on cream (~4.6:1); was '#D85A4E' (4.1:1 fail)
    bg     = '#FAF6EC',   # main light background — was '#E3F1FA' (light blue)
    white  = '#FFFFFF',
    muted  = '#6B7C93',
    border = '#E5DDCB',   # warm border to match cream bg
    light  = '#FDFAF3',   # very light warm cream
    slate  = '#4A5A6E',   # secondary text from PPT
)

MMM_COLOURS = {
    # Single navy → teal ramp so all 7 bands sit on one continuous remoteness scale.
    # Anchored at PPT-matched navy '#11304E' and teal '#2BA39B'.
    'MM1': '#11304E', 'MM2': '#264E78', 'MM3': '#3D6FA0',
    'MM4': '#5F92BC', 'MM5': '#85B4C5', 'MM6': '#9CC9C0', 'MM7': '#2BA39B',
}

ORG_COLOURS = {
    'profit':         '#E67E22',   # orange — distinct from red (alert/crisis only)
    'not_for_profit': '#11304E',   # PPT-synced navy
    'government':     '#2BA39B',   # PPT-synced teal
}

SNAP_YEAR = {
    'May 2023': 2023, 'August 2023': 2023, 'December 2023': 2023,
    'February 2024': 2024, 'May 2024': 2024, 'July 2024': 2024, 'November 2024': 2024,
    'February 2025': 2025, 'May 2025': 2025, 'August 2025': 2025, 'October 2025': 2025,
    'February 2026': 2026,
}

MANDATE = pd.Timestamp('2023-10-01')

# ── Ch5 Forecast — 2025 population projection scenarios ───────────────────────
SCENARIO_GROWTH_RATES = {
    'Baseline (ABS trend)':   None,
    'Aggressive aging (+4%)': 0.04,
    'Stagnation (0%)':        0.00,
}


def state_cagr_2019_2024(population: pd.DataFrame) -> dict:
    """Per-state compound annual growth rate of pop_65_plus from 2019 to 2024.
    Used as the Baseline scenario for projecting 2025.
    Fallback rate 0.024 (~ABS national trend) if either endpoint missing."""
    agg = population.groupby(['state', 'year'])['pop_65_plus'].sum().reset_index()
    rates = {}
    for state in agg['state'].dropna().unique():
        s = agg[agg['state'] == state]
        start = s[s['year'] == 2019]['pop_65_plus'].sum()
        end   = s[s['year'] == 2024]['pop_65_plus'].sum()
        if start > 0 and end > 0:
            rates[state] = (end / start) ** (1 / 5) - 1
        else:
            rates[state] = 0.024
    return rates


def project_pop_65_2025(population: pd.DataFrame, scenario: str) -> pd.DataFrame:
    """Return DataFrame with columns sa3_code, state, pop_65_plus_2024, pop_65_plus_2025,
    growth_rate. Baseline uses per-state CAGR; Aggressive +4%; Stagnation 0%."""
    base = population[population['year'] == 2024][['sa3_code', 'state', 'pop_65_plus']].copy()
    base = base.rename(columns={'pop_65_plus': 'pop_65_plus_2024'})

    g = SCENARIO_GROWTH_RATES[scenario]
    if g is None:
        rates = state_cagr_2019_2024(population)
        base['growth_rate'] = base['state'].map(rates).fillna(0.024)
    else:
        base['growth_rate'] = g

    base['pop_65_plus_2025'] = base['pop_65_plus_2024'] * (1 + base['growth_rate'])
    return base


def build_master_2025(master, supply, service_users, ratings, population, scenario):
    """Build a synthetic 2025 master row per SA3:
      pop_65_plus  → projected via scenario
      total_residential, hcp_high_needs → real 2025 from service_users
      residential_places, n_facilities → real 2025 from supply
      quality_score → mean of latest 2025 snapshot from ratings (if any) or carry 2024
      Recompute: access_rate, care_gap_index, beds_per_1k, waitlist_pressure.
    Returns DataFrame ready to feed the choropleth."""
    proj = project_pop_65_2025(population, scenario)

    su = service_users[service_users['year'] == 2025][
        ['sa3_code', 'total_residential', 'hcp_high_needs']
    ].copy()

    sp = supply[supply['year'] == 2025][
        ['sa3_code', 'residential_places', 'n_facilities']
    ].copy()

    # 2024 quality from master as default; if ratings has 2025 snapshots, use mean
    q24 = master[master['year'] == 2024][['sa3_code', 'quality_score']].copy()
    q24 = q24.rename(columns={'quality_score': 'quality_2024'})
    if 'snap_year' in ratings.columns and (ratings['snap_year'] == 2025).any() and 'sa3_code' in ratings.columns:
        q25 = (
            ratings[ratings['snap_year'] == 2025]
            .groupby('sa3_code')['quality_score']
            .mean()
            .reset_index()
            .rename(columns={'quality_score': 'quality_2025'})
        )
    else:
        q25 = pd.DataFrame(columns=['sa3_code', 'quality_2025'])

    meta = master[['sa3_code', 'sa3_name', 'state', 'mmm_code']].drop_duplicates('sa3_code')

    df = (
        proj
        .merge(meta, on=['sa3_code', 'state'], how='left')
        .merge(su, on='sa3_code', how='left')
        .merge(sp, on='sa3_code', how='left')
        .merge(q24, on='sa3_code', how='left')
        .merge(q25, on='sa3_code', how='left')
    )

    df['quality_score'] = df['quality_2025'].fillna(df['quality_2024'])

    df['access_rate'] = (df['total_residential'] / df['pop_65_plus_2025']) * 100
    df['care_gap_index'] = df['access_rate'] / df['quality_score'].replace(0, pd.NA)
    df['beds_per_1k'] = (df['residential_places'] / df['pop_65_plus_2025']) * 1000
    df['waitlist_pressure'] = df['hcp_high_needs'] / df['residential_places']

    return df


_FONT = 'Inter,-apple-system,BlinkMacSystemFont,sans-serif'
_AXIS = dict(
    gridcolor=C['bg'],
    linecolor=C['border'],
    tickcolor=C['border'],
    tickfont=dict(color=C['navy'], size=15, family=_FONT),
    title_font=dict(color=C['navy'], size=16, family=_FONT),
)


def theme(fig, height=None):
    """Apply consistent Plotly chart theme."""
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family=_FONT, color=C['navy'], size=16),
        title_font=dict(size=19, color=C['navy'], family=_FONT),
        margin=dict(l=0, r=16, t=56, b=8),
        legend=dict(
            bgcolor='rgba(255,255,255,0.92)',
            bordercolor=C['border'],
            borderwidth=1,
            font=dict(color=C['navy'], size=15),
        ),
        xaxis=_AXIS,
        yaxis=_AXIS,
    )
    # Force all axes on multi-axis charts (yaxis2, yaxis3, etc.)
    for ax in ['xaxis2', 'yaxis2', 'xaxis3', 'yaxis3']:
        if hasattr(fig.layout, ax):
            fig.update_layout(**{ax: _AXIS})
    if height:
        fig.update_layout(height=height)
    return fig


# ── Chapter breadcrumb (top of each chapter page) ──────────────────────────
_CHAPTERS = [
    (1, 'map',         'The Gap'),
    (2, 'correlation', 'The Cause'),
    (3, 'reveal',      'The Victims'),
    (4, 'mandate',     'The Verdict'),
]


def chapter_breadcrumb(current: int) -> str:
    """Return HTML for the chapter-progress breadcrumb shown at top of each chapter.
    Pass the chapter number (1–4) currently being viewed."""
    crumbs = []
    for num, page, name in _CHAPTERS:
        if num == current:
            crumbs.append(
                f'<span style="background:{C["navy"]};color:white;padding:3px 10px;'
                f'border-radius:8px;font-weight:700;font-size:13px">'
                f'{num}. {name}</span>'
            )
        else:
            crumbs.append(
                f'<a href="?page={page}" target="_self" '
                f'style="color:{C["muted"]};text-decoration:none;padding:3px 10px;'
                f'font-size:13px">{num}. {name}</a>'
            )
    sep = '<span style="color:#E5DDCB">·</span>'
    return (
        f'<div style="display:flex;gap:4px;align-items:center;flex-wrap:wrap;'
        f'margin:0 0 14px;font-size:13px;color:{C["muted"]}">'
        f'<a href="?page=home" target="_self" '
        f'style="color:{C["muted"]};text-decoration:none;padding:3px 8px">🏠 Home</a>'
        f'<span style="color:#E5DDCB">›</span>'
        f'{sep.join(crumbs)}'
        f'</div>'
    )


# ── Chapter closer: Key takeaways + Next-chapter CTA ──────────────────────
_NEXT_PREVIEW = {
    1: 'Why some areas have the gap — ownership, funding, and quality',
    2: 'Who pays the price when access falls behind demand',
    3: 'Whether the Oct 2023 staffing mandate actually moved the needle',
    4: None,  # last chapter — link back to Home instead
}


def chapter_closer(current: int, takeaways: list[str]) -> str:
    """Render the bottom-of-chapter block: '💡 Key takeaways' bullets +
    a large 'Next chapter →' CTA card (or 'Back to Home' on the final chapter)."""
    # ── Key takeaways block ────────────────────────────────────────────
    bullets_html = ''.join(
        f'<li style="margin:6px 0;padding-left:6px">{t}</li>' for t in takeaways
    )
    takeaways_html = (
        f'<div style="background:#FBF6E5;border-left:5px solid {C["gold"]};'
        f'border-radius:8px;padding:16px 22px;margin:24px 0 18px;'
        f'color:{C["navy"]};font-size:18px;line-height:1.55">'
        f'<div style="font-weight:800;font-size:15px;letter-spacing:0.04em;'
        f'text-transform:uppercase;color:#8B6914;margin-bottom:8px">'
        f'💡 Key takeaways</div>'
        f'<ul style="margin:0;padding-left:22px">{bullets_html}</ul>'
        f'</div>'
    )

    # ── Next-chapter CTA card (or back-to-home on final chapter) ──────
    if current >= 4 or _NEXT_PREVIEW.get(current) is None:
        cta_label = '🏠 Back to overview'
        cta_target = 'home'
        cta_preview = 'Return to the national scoreboard and explore other chapters.'
        cta_kicker = 'Wrap-up'
    else:
        nxt_num = current + 1
        nxt_page, nxt_name = _CHAPTERS[nxt_num - 1][1], _CHAPTERS[nxt_num - 1][2]
        cta_label = f'Chapter {nxt_num}: {nxt_name} →'
        cta_target = nxt_page
        cta_preview = _NEXT_PREVIEW[current]
        cta_kicker = f'Next · Chapter {nxt_num} of 4'

    cta_html = (
        f'<a href="?page={cta_target}" target="_self" '
        f'style="display:block;text-decoration:none;color:inherit">'
        f'<div style="background:{C["navy"]};color:white;border-radius:10px;'
        f'padding:20px 26px;margin:0 0 8px;display:flex;align-items:center;'
        f'justify-content:space-between;gap:18px;transition:transform 0.15s ease">'
        f'<div>'
        f'<div style="font-size:13px;font-weight:700;letter-spacing:0.06em;'
        f'text-transform:uppercase;opacity:0.65;margin-bottom:6px">{cta_kicker}</div>'
        f'<div style="font-size:24px;font-weight:800;margin-bottom:4px">{cta_label}</div>'
        f'<div style="font-size:16px;opacity:0.85;font-weight:400">{cta_preview}</div>'
        f'</div>'
        f'<div style="font-size:38px;opacity:0.85">›</div>'
        f'</div>'
        f'</a>'
    )

    return takeaways_html + cta_html


# ── Data source caption (under each chart) ──────────────────────────────────
def data_caption(sources: str | None = None) -> str:
    """HTML caption for use after st.plotly_chart so viewers can verify data vintage.
    Usage: st.markdown(data_caption(), unsafe_allow_html=True)
           st.markdown(data_caption("ACQSC Star Ratings, May 2023–Feb 2026"), unsafe_allow_html=True)
    """
    if sources is None:
        sources = ("ACQSC Star Ratings (Feb 2026 snapshot) · "
                   "ABS Population SA3 2019–2024 · AIHW GEN (residential & home care)")
    return f'<p class="data-caption">📊 Source: {sources}.</p>'
