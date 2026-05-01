# Chapter 2 — The Correlation: Does high demand cause low quality?

## Narrative purpose
The second clue. After seeing the map, the viewer asks: "Why do some regions have such a large gap?" This chapter answers by showing the relationship between utilisation and quality — and where vulnerable communities (NESB, Indigenous, Remote) sit within that picture.

---

## Visual: Scatter plot

- **X-axis:** `access_rate` (% of 65+ population using residential care)
- **Y-axis:** `quality_score` (mean of 4 Star Rating sub-dimensions)
- **Size:** `pop_65_plus`
- **Colour:** MMM remoteness (MM1–MM7) or state
- **Hover:** SA3 name, state, MMM, access_rate, quality_score, pop_65_plus

---

## Data available

| File | Columns needed |
|------|---------------|
| `data/clean/stars_timeline.csv` | `sa3_code`, `year`, `quality_score`, `mmm_code` |
| `data/clean/access_sa3.csv` | `sa3_code`, `year`, `care_type`, `total_users` |
| `data/raw/population/` | `sa3_code`, `sa3_name`, `state`, `pop_65_plus` |

Use the same `df` built in Chapter 1 — it already has `access_rate`, `avg_quality`, `pop_65_plus`, and `mmm_code`.

---

## How to build the scatter

```python
import plotly.express as px

fig = px.scatter(
    df[df['year'] == selected_year],
    x='access_rate',
    y='avg_quality',
    size='pop_65_plus',
    color='mmm_code',
    hover_name='sa3_name',
    hover_data={
        'state': True,
        'access_rate': ':.1f',
        'avg_quality': ':.2f',
        'pop_65_plus': ':,',
    },
    trendline='ols',
    labels={
        'access_rate': 'Access Rate (% of 65+ in residential care)',
        'avg_quality': 'Quality Score (avg Star Rating sub-dimensions)',
        'mmm_code':    'Remoteness',
    },
    title=f'Access Rate vs Quality Score by SA3 ({selected_year})',
)
st.plotly_chart(fig, use_container_width=True)
```

---

## Demographic overlay (optional toggle)

Add a colour/highlight option to surface NESB and Indigenous communities within the scatter.

```python
# Join SA3 → ACPR → demographics
df = df.merge(sa3_acpr[['sa3_code', 'acpr_code']], on='sa3_code', how='left')
df = df.merge(
    demographics[demographics['year'] == selected_year][
        ['acpr_code', 'pct_nesb', 'pct_indigenous']
    ],
    on='acpr_code', how='left'
)

# Flag NESB-majority communities
df['nesb_flag'] = df['pct_nesb'] > 0.30
```

---

## Key insights to surface

- Negative trend line: higher access_rate correlates with lower quality_score — the system is stretched
- Remote regions cluster in the top-right danger zone: high access AND low quality
- NESB-heavy regions tend to have lower-than-expected access rate — possible underutilisation
- Sydney and Melbourne: low access rate but high quality — serving those who already have access well
