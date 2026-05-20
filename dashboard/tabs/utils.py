"""Shared constants, colour maps, and Plotly theme for the DVN AT3 dashboard."""

import pandas as pd

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
    df['care_gap_index'] = df['access_rate'] / df['quality_score']
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
