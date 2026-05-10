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


def theme(fig, height=None):
    """Apply consistent Plotly chart theme."""
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family='Inter,-apple-system,BlinkMacSystemFont,sans-serif',
            color=C['navy'], size=12,
        ),
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
