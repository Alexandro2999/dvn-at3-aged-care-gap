# Chapter 3 — The Reveal: These are the communities being left behind

## Narrative purpose
The climax. After the map and the correlation, the viewer needs a concrete list: "Which are the 20 worst regions?" More importantly: "Who actually lives there?" This chapter connects the care gap to real people — NESB communities, Indigenous Australians, those stuck waiting on high-level HCP packages.

---

## Visual A: Ranked horizontal bar chart (Top 20 worst SA3)

- **X-axis:** `care_gap_index`
- **Y-axis:** SA3 name (sorted descending)
- **Colour:** MMM remoteness or state
- **Hover:** access_rate, quality_score, pop_65_plus, state

```python
import plotly.express as px

worst20 = df[df['year'] == selected_year].nlargest(20, 'care_gap_index')

fig = px.bar(
    worst20.sort_values('care_gap_index'),
    x='care_gap_index',
    y='sa3_name',
    orientation='h',
    color='mmm_code',
    hover_data={'access_rate': ':.1f', 'avg_quality': ':.2f', 'state': True},
    title='Top 20 Most Underserved Regions',
    labels={'care_gap_index': 'Care Gap Index', 'sa3_name': ''},
)
st.plotly_chart(fig, use_container_width=True)
```

---

## Visual B: Demographic detail card

When a user clicks an SA3 in the bar chart, show a detail panel:

| Metric | Source column |
|--------|--------------|
| % NESB residents | `pct_nesb` from `demographics_acpr.csv` |
| % Indigenous residents | `pct_indigenous` |
| % new care entrants this year | `pct_first_admission` |
| HCP level distribution | `hcp_l1`, `hcp_l2`, `hcp_l3`, `hcp_l4` |

---

## Data available

| File | Columns needed |
|------|---------------|
| `care_gap_index` df from Chapter 1 | `sa3_code`, `year`, `care_gap_index`, `mmm_code`, `state` |
| `data/clean/demographics_acpr.csv` | `acpr_code`, `year`, `pct_nesb`, `pct_indigenous`, `pct_first_admission`, `hcp_l1–l4` |

**Note on geography mismatch:** Demographics are at ACPR level (73 regions), not SA3 (358 regions). Need a SA3 → ACPR correspondence to join.

```python
# SA3 → ACPR mapping — source from service list or ABS correspondence file
sa3_acpr = pd.read_csv('data/raw/geography/sa3_acpr_correspondence.csv')

df = df.merge(sa3_acpr[['sa3_code', 'acpr_code']], on='sa3_code', how='left')
df = df.merge(
    demographics[demographics['year'] == selected_year][[
        'acpr_code', 'pct_nesb', 'pct_indigenous', 'pct_first_admission',
        'hcp_l1', 'hcp_l2', 'hcp_l3', 'hcp_l4'
    ]],
    on='acpr_code', how='left'
)
```

---

## Visual C: HCP level stacked bar (optional)

For the top 20 regions, show the distribution of HCP Levels 1–4.
Level 3 + Level 4 heavy = many people waiting for residential care, stuck in home care.

```python
hcp_cols = ['hcp_l1', 'hcp_l2', 'hcp_l3', 'hcp_l4']
fig = px.bar(
    worst20_with_demo,
    x='sa3_name',
    y=hcp_cols,
    barmode='stack',
    title='HCP Level Distribution — Top 20 Worst Regions',
    labels={'value': 'Users', 'variable': 'HCP Level'},
)
```

---

## Key insights to surface

- Most of the top 20 worst SA3 regions fall in Remote or Very Remote (MM5–MM7)
- Regions with high `pct_nesb` tend to show low `pct_first_admission` — NESB communities are less likely to enter the system for the first time
- High `hcp_l3 + hcp_l4` share in rural regions suggests unmet demand for residential care — people need it but can't access it
