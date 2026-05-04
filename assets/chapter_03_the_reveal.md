# Chapter 3 — The Reveal: The waitlist is real — and it's getting longer

## Narrative purpose
Numbers become people. This chapter names the 20 regions where elderly Australians with high care needs are stuck waiting — often over a year — because there simply aren't enough beds. For families, it's a warning about which areas to avoid or plan around. For businesses and workers entering the sector, it's the clearest possible signal of where demand is outstripping supply.

---

## Visual A: Ranked horizontal bar chart (Top 20 worst SA3 by waitlist pressure)

- **X-axis:** `waitlist_pressure` (HCP high-needs users per residential bed)
- **Y-axis:** SA3 name (sorted descending)
- **Colour:** MMM remoteness or state
- **Hover:** access_rate, avg_quality, pop_65_plus, state

```python
import plotly.express as px

worst20 = df[df['year'] == selected_year].nlargest(20, 'waitlist_pressure')

fig = px.bar(
    worst20.sort_values('waitlist_pressure'),
    x='waitlist_pressure',
    y='sa3_name',
    orientation='h',
    color='mmm_code',
    hover_data={'access_rate': ':.1f', 'avg_quality': ':.2f', 'state': True},
    title='Top 20 Regions by Waitlist Pressure (HCP high-needs per residential bed)',
    labels={'waitlist_pressure': 'HCP High-Needs per Residential Bed', 'sa3_name': ''},
)
st.plotly_chart(fig, use_container_width=True)
```

---

## Visual B: HCP level stacked bar

For the top 20 regions, show the distribution of HCP Levels 1–4.
Level 3 + Level 4 heavy = many people waiting for residential care, stuck in home care.

```python
hcp_cols = ['hcp_level1', 'hcp_level2', 'hcp_level3', 'hcp_level4']

fig = px.bar(
    worst20,
    x='sa3_name',
    y=hcp_cols,
    barmode='stack',
    title='HCP Level Distribution — Top 20 Highest Waitlist Pressure Regions',
    labels={'value': 'Users', 'variable': 'HCP Level'},
)
st.plotly_chart(fig, use_container_width=True)
```

---

## Data available

| File | Columns needed |
|------|---------------|
| `data/clean/service_users_by_sa3.csv` | `sa3_code`, `year`, `total_residential`, `hcp_level1`–`hcp_level4`, `hcp_high_needs` |
| `data/clean/service_supply_by_sa3.csv` | `sa3_code`, `year`, `residential_places` |
| `data/clean/abs_population_by_sa3.csv` | `sa3_code`, `sa3_name`, `state`, `year`, `pop_65_plus` |

```python
# waitlist_pressure = HCP high-needs per residential bed
df = df.merge(
    supply[['sa3_code', 'year', 'residential_places']],
    on=['sa3_code', 'year']
)
df['waitlist_pressure'] = df['hcp_high_needs'] / df['residential_places']
```

---

## Key insights to surface

- **Noosa Hinterland: 313 people needing high-level care for every 1 residential bed** — the most extreme case nationally (Feb 2026). If your family member needs a high-care bed here, the queue is effectively infinite.
- **The high-needs waitlist grew 22% in just 2 years** — from 140,000 (2023) to 172,000 (2025). These are people approved for Level 3–4 packages who cannot get residential care. 59% of all home care approvals are now at this level.
- **118 regions lost residential facilities** between 2019 and 2025 while demand surged — net −41 regions nationally. For businesses: these are not saturated markets, they are abandoned ones.
- For workers: entering the sector in a high-pressure region means job security and urgency. The shortage is not a future problem — it's already here.

---

## Note: Demographic data limitation

NESB and Indigenous demographic data is available at **ACPR level only (73 regions)** — it cannot be joined to SA3 (358 regions). Do not build a demographic detail card at SA3 level. If a demographic angle is needed, scope it as a separate ACPR-level chart, clearly labelled as a different geographic unit.
