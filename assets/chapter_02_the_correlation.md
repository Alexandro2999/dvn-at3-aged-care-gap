# Chapter 2 — The Correlation: Who runs the best facilities?

## Narrative purpose
After seeing the map, the viewer asks: "Why is quality so different across regions?" This chapter gives the answer most people don't expect — it's not about location, it's about who owns the facility. Government and not-for-profit facilities consistently outperform private ones. The geography story is really an ownership story.

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

- **Counterintuitive for families:** rural and remote areas score *higher* on quality (MM5 = 4.05 vs MM1 City = 3.75) — if your family member is in a regional facility, it's likely run by a charity or government and performing better than a city competitor.
- **The ownership gap is stark:** government-run facilities average 4.21 stars vs for-profit 3.68 — a 0.53 gap. For families choosing a facility, who owns it is a strong quality signal.
- **For investors considering the sector:** metro areas are 42% for-profit and showing lower quality — there is a real opportunity to compete on care standards, not just on price or location. Rural markets are almost entirely NFP/government — an untapped space.

---

## Note on demographic overlay

NESB and Indigenous demographic data (from CURF) is only available at **ACPR level (73 regions)**, not SA3. Do not attempt to join it to SA3 — the correspondence does not exist in our pipeline. Any demographic angle must be scoped to ACPR-level analysis only.
