# Chapter 2 — The Correlation: Who runs the best facilities?

## Narrative purpose
After seeing the map, the viewer asks: "Why is quality so different across regions?" This chapter gives the answer most people don't expect — it's not about location, it's about who owns the facility. Government and not-for-profit facilities consistently outperform private ones. The geography story is really an ownership story.

---

## Visual A: Scatter plot — Access Rate vs Quality (with year slider)

- **X-axis:** `access_rate` (% of 65+ population in residential care)
- **Y-axis:** `avg_quality` (mean of 4 Star Rating sub-dimensions)
- **Size:** `pop_65_plus`
- **Colour:** MMM remoteness (MM1–MM7)
- **Interaction:** Year slider (2023–2024), OLS trendline
- **Hover:** SA3 name, state, remoteness, access_rate, avg_quality, pop_65_plus, n_facilities

```python
fig = px.scatter(
    df[df['year'] == selected_year],
    x='access_rate', y='avg_quality',
    size='pop_65_plus', color='mmm_code',
    category_orders={'mmm_code': ['MM1','MM2','MM3','MM4','MM5','MM6','MM7']},
    hover_name='sa3_name',
    hover_data={'state': True, 'access_rate': ':.1f', 'avg_quality': ':.2f', 'pop_65_plus': ':,'},
    trendline='ols',
    title=f'Access Rate vs Quality Score by SA3 ({selected_year})',
)
st.plotly_chart(fig, use_container_width=True)
```

---

## Visual B: Grouped bar — Ownership quality within each MMM band

Directly controls for geography: government outperforms for-profit inside every remoteness band.

- **X-axis:** MMM remoteness band (MM1–MM7)
- **Y-axis:** `avg_quality`
- **Colour:** Ownership type (Government / Not-for-Profit / For-Profit)
- **Interaction:** Follow sidebar year filter

```python
fig = px.bar(
    ownership_mmm,
    x='mmm_code', y='avg_quality', color='purpose_clean',
    barmode='group',
    category_orders={'mmm_code': mmm_order, 'purpose_clean': purpose_order},
    color_discrete_map=colour_purpose,
    title="Ownership Gap Persists Across All Remoteness Bands — it's not just geography",
)
st.plotly_chart(fig, use_container_width=True)
```

---

## Visual C: Grouped bar — Sub-rating breakdown by ownership type

Shows which of the 4 star rating dimensions drives the ownership gap.

- **X-axis:** Star rating dimension (Staffing, Residents' Experience, Compliance, Quality Measures)
- **Y-axis:** Average score
- **Colour:** Ownership type (Government / Not-for-Profit / For-Profit)

```python
fig = px.bar(
    subrating_data,
    x='subrating_label', y='avg_score', color='purpose_clean',
    barmode='group',
    title='Sub-rating Breakdown by Ownership Type — where does the gap come from?',
)
st.plotly_chart(fig, use_container_width=True)
```

---

## Visual D: Horizontal bar — Funding per facility by org type

- **X-axis:** Average government funding per facility ($M, 2024)
- **Y-axis:** Ownership type
- **Annotation inline:** avg quality score per type
- **Colour:** Ownership type

```python
fig = go.Figure()
for _, row in funding_per_facility.iterrows():
    fig.add_trace(go.Bar(
        x=[row['funding_per_facility_m']], y=[row['label']], orientation='h',
        text=[f"${row['funding_per_facility_m']:.2f}M | quality {row['avg_quality']:.2f}"],
    ))
st.plotly_chart(fig, use_container_width=True)
```

---

## Data available

| File | Columns needed |
|------|---------------|
| `data/clean/star_ratings_by_facility.csv` | `sa3_code`, `sa3_name`, `state`, `mmm_code`, `snapshot_date`, `quality_score`, `residents_exp`, `staffing`, `compliance`, `quality_measures`, `Purpose` |
| `data/clean/service_users_by_sa3.csv` | `sa3_code`, `year`, `total_residential`, `total_homecare` |
| `data/clean/abs_population_by_sa3.csv` | `sa3_code`, `year`, `pop_65_plus` |
| `data/clean/service_funding_by_facility.csv` | `sa3_code`, `year`, `org_type`, `funding`, `service_name` |

```python
# access_rate = residential users as % of 65+ population
df = users.merge(pop, on=['sa3_code', 'year'])
df['access_rate'] = df['total_residential'] / df['pop_65_plus'] * 100

# avg_quality per SA3 × year
quality = ratings.groupby(['sa3_code', 'year'])['quality_score'].mean().reset_index()
df = df.merge(quality, on=['sa3_code', 'year'])

# normalise Purpose casing before grouping by ownership
ratings['purpose_clean'] = ratings['Purpose'].str.strip().str.lower().map({
    'for profit': 'For-Profit', 'not for profit': 'Not-for-Profit', 'government': 'Government',
})
```

---

## Key insights to surface

- **The ownership gap is 0.57 stars:** Government-run facilities average **4.07** vs for-profit **3.50** across all 12 quarterly snapshots (May 2023 → Feb 2026). The gap has not narrowed since the Oct 2023 staffing mandate.
- **Staffing drives the entire gap:** Government scores **4.39 on staffing** vs for-profit **2.61** — a 1.78-point difference. Health outcomes (Quality Measures) are virtually identical at 3.52 vs 3.51. For-profit facilities are not delivering worse clinical outcomes; they are deploying fewer staff hours.
- **The gap is not a geography artefact:** Within MM1 major cities, government scores 4.03 vs for-profit 3.50. In MM5 small rural towns, government scores 4.19 vs for-profit 3.63 — the gap *widens* in rural areas. Ownership type predicts quality inside every remoteness band.
- **Metro = most privatised = lowest quality:** For-profit makes up **43.6% of MM1 facilities**, falling to 0% in MM6 and MM7. This is why the Chapter 1 map shows city patches of low quality — it's a concentration-of-for-profit problem, not a city infrastructure problem.
- **For-profit receives the most public funding per facility:** $7.46M per facility in 2024, vs $5.54M (NFP) and $2.85M (Government). The most publicly subsidised type produces the least quality — the efficiency argument for privatisation does not hold in this data.

---

## Note on demographic overlay

NESB and Indigenous demographic data (from CURF) is only available at **ACPR level (73 regions)**, not SA3. Do not attempt to join it to SA3 — the correspondence does not exist in the pipeline. Any demographic angle must be scoped to ACPR-level analysis only.
