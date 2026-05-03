# Chapter 2 — The Correlation: Does ownership and location explain quality?

## Narrative purpose
The second clue. After seeing the map, the viewer asks: "Why do some regions have such a large gap?" This chapter answers by showing the relationship between access, quality, and remoteness — and reveals the ownership paradox: remote areas score *higher* because they have fewer for-profit facilities.

---

## Visual: Scatter plot

- **X-axis:** `access_rate` (% of 65+ population using residential care)
- **Y-axis:** `avg_quality` (mean of 4 Star Rating sub-dimensions)
- **Size:** `pop_65_plus`
- **Colour:** MMM remoteness (MM1–MM7) or org type
- **Hover:** SA3 name, state, MMM, access_rate, avg_quality, pop_65_plus

---

## Data available

| File | Columns needed |
|------|---------------|
| `data/clean/star_ratings_by_facility.csv` | `sa3_code`, `year`, `quality_score`, `mmm_code` |
| `data/clean/service_users_by_sa3.csv` | `sa3_code`, `year`, `total_residential` |
| `data/clean/abs_population_by_sa3.csv` | `sa3_code`, `sa3_name`, `state`, `year`, `pop_65_plus` |

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

## Key insights to surface

- **Remote areas (MM5–MM7) sit in the top-left: low access, high quality** — the opposite of the intuitive assumption. MM5 Small Rural = 4.05, MM1 City = 3.75.
- **The remote quality advantage is explained by ownership mix** — MM1 City is 42% for-profit, 57% NFP; MM6–7 Remote is 0% for-profit (~70% NFP, ~30% govt). For-profit facilities average 3.68 vs govt 4.21.
- **Metro areas cluster bottom-right: high access, lower quality** — densely served but served by a higher share of for-profit providers
- The ownership story (Chapter angle: For-Profit Problem) explains the geography story

---

## Note on demographic overlay

NESB and Indigenous demographic data (from CURF) is only available at **ACPR level (73 regions)**, not SA3. Do not attempt to join it to SA3 — the correspondence does not exist in our pipeline. Any demographic angle must be scoped to ACPR-level analysis only.
