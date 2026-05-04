# Chapter 1 — The Map: Is aged care near me any good?

## Narrative purpose
Open with a map that lets the viewer locate what matters to them — their suburb, their parents' city, their potential market. Before reading a single number, they can see their region and ask: "Is the care near me actually decent — and is there enough of it?" The map answers both questions at once.

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

- **For families:** the worst-served regions are often not remote — they're metro areas packed with facilities that score lower on quality because for-profit providers dominate. More choice doesn't mean better care.
- **For people in rural areas:** fewer beds nearby, but the ones that exist tend to score higher. The real disadvantage is distance and availability — not the standard of care itself.
- **For businesses and investors:** two distinct market gaps exist — metro areas with high demand but declining quality (room to compete on quality), and rural/remote areas where almost no private operators exist and unmet demand is growing.
