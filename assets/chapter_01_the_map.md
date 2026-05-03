# Chapter 1 — The Map: Where is the crisis?

## Narrative purpose
The first clue. The viewer sees a map of Australia and immediately spots which regions are being left behind. The question it raises: "Which communities are under the most pressure?"

---

## Visual: Choropleth map

Each SA3 is coloured by `care_gap_index`. Darker colour (red/orange) = more underserved.

**Interactions:**
- Hover: SA3 name, state, care_gap_index, quality_score, access_rate, pop_65_plus
- Sidebar filters: State, Remoteness (MMM), Year

---

## Data available

| File | Columns needed |
|------|---------------|
| `data/clean/star_ratings_by_facility.csv` | `sa3_code`, `sa3_name`, `state`, `mmm_code`, `snapshot_date`, `quality_score` |
| `data/clean/service_users_by_sa3.csv` | `sa3_code`, `year`, `total_residential` |
| `data/clean/abs_population_by_sa3.csv` | `sa3_code`, `year`, `pop_65_plus` |
| `data/raw/abs_geography/` | SA3 shapefile (GeoJSON or SHP from ABS) |

---

## How to compute care_gap_index

```python
# Step 1: access_rate — residential users as % of 65+ population
users = service_users[['sa3_code', 'year', 'total_residential']]
pop   = abs_pop[['sa3_code', 'year', 'pop_65_plus']]

df = users.merge(pop, on=['sa3_code', 'year'])
df['access_rate'] = df['total_residential'] / df['pop_65_plus'] * 100

# Step 2: quality_score — mean across all facilities and quarters per SA3 × year
quality = (
    ratings.groupby(['sa3_code', 'year'])['quality_score']
    .mean()
    .reset_index()
    .rename(columns={'quality_score': 'avg_quality'})
)

# Step 3: care_gap_index
df = df.merge(quality, on=['sa3_code', 'year'])
df['care_gap_index'] = df['access_rate'] / df['avg_quality']
```

---

## How to build the map

```python
import geopandas as gpd
import plotly.express as px

gdf = gpd.read_file('data/raw/abs_geography/SA3_2021_AUST_GDA2020.shp')
gdf = gdf.rename(columns={'SA3_CODE21': 'sa3_code'})
gdf['sa3_code'] = gdf['sa3_code'].astype(int)

merged = gdf.merge(df[df['year'] == selected_year], on='sa3_code', how='left')

fig = px.choropleth(
    merged,
    geojson=merged.geometry,
    locations=merged.index,
    color='care_gap_index',
    color_continuous_scale='YlOrRd',
    hover_data={'sa3_name': True, 'state': True, 'access_rate': ':.1f', 'avg_quality': ':.2f'},
    title=f'Care Gap Index by SA3 ({selected_year})',
)
fig.update_geos(fitbounds='locations', visible=False)
st.plotly_chart(fig, use_container_width=True)
```

---

## Key insights to surface

- **High care_gap_index = high access but lower quality** — formula is `access_rate / quality_score`, so metro areas with dense for-profit supply appear high
- **Remote areas are NOT the worst by this metric** — remote SA3s have *higher* quality (MM5 = 4.05) but *lower* access; their care_gap_index is lower, but their access crisis is real and better captured by `waitlist_pressure` and `beds_per_1000_elderly`
- The map reveals two different types of underserved regions: high-access/low-quality (metro) and low-access/high-quality (remote) — the story differs by region type
