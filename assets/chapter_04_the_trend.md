# Chapter 4 — The Trend: Is it getting better?

## Narrative purpose
The final clue — and the call to action. After identifying where and who, the viewer asks: "Is anyone doing something about it?" This chapter shows whether quality has improved over time, and whether the October 2023 staffing mandate actually moved the needle. The answer determines how urgent the story ends.

---

## Visual: Line chart — Average quality score over time

- **X-axis:** time (quarterly, May 2023 → Feb 2026)
- **Y-axis:** average `quality_score`
- **Colour:** state or MMM remoteness group
- **Key annotation:** vertical line at October 2023 (staffing mandate came into effect)

```python
import plotly.express as px
import plotly.graph_objects as go

# Aggregate to state × quarter
trend = (
    stars.groupby(['state', 'year', 'quarter'])['quality_score']
    .mean()
    .reset_index()
)
trend['period'] = trend['year'].astype(str) + '-Q' + trend['quarter'].astype(str)

fig = px.line(
    trend,
    x='period',
    y='quality_score',
    color='state',
    markers=True,
    title='Average Quality Score Over Time by State',
    labels={'quality_score': 'Avg Quality Score', 'period': 'Quarter'},
)

# Mark Oct 2023 staffing mandate
fig.add_vline(
    x='2023-Q4',
    line_dash='dash',
    line_color='red',
    annotation_text='Staffing mandate (Oct 2023)',
    annotation_position='top left',
)

st.plotly_chart(fig, use_container_width=True)
```

---

## Alternative view: By remoteness group

Instead of state, colour by MMM group to show whether the mandate helped remote regions more or less than cities.

```python
# Collapse MM codes into 3 groups for readability
stars['remoteness_group'] = stars['mmm_code'].map({
    'MM1': 'Metropolitan',
    'MM2': 'Metropolitan',
    'MM3': 'Regional',
    'MM4': 'Regional',
    'MM5': 'Remote',
    'MM6': 'Remote',
    'MM7': 'Remote',
})

trend_mmm = (
    stars.groupby(['remoteness_group', 'year', 'quarter'])['quality_score']
    .mean()
    .reset_index()
)
```

---

## Data available

| File | Columns needed |
|------|---------------|
| `data/clean/stars_timeline.csv` | `sa3_code`, `state`, `mmm_code`, `year`, `quarter`, `quality_score`, `staffing`, `residents_exp`, `compliance`, `quality_measures` |

This chapter uses `stars_timeline.csv` only — no join required.

---

## Optional: Sub-dimension breakdown

Show how each of the 4 sub-dimensions changed over time — useful to see whether `staffing` specifically improved post-mandate while others lagged.

```python
sub_dims = ['residents_exp', 'staffing', 'compliance', 'quality_measures']

trend_sub = (
    stars.groupby(['year', 'quarter'])[sub_dims]
    .mean()
    .reset_index()
)

fig = px.line(
    trend_sub.melt(id_vars=['year', 'quarter'], value_vars=sub_dims),
    x='quarter',  # or use a combined period column
    y='value',
    color='variable',
    facet_col='year',
    title='Quality Sub-dimensions Over Time (National)',
)
```

---

## Key insights to surface

- Did `staffing` scores rise after Oct 2023? If yes — mandate had measurable impact
- Did remote regions benefit as much as cities? Likely not — staffing shortage is worse in remote areas
- Overall trend direction sets the tone for the ending: improving = cautious optimism / flat or declining = urgent call to action
