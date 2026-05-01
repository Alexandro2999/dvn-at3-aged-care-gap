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
| `data/clean/stars_timeline.csv` | `sa3_code`, `sa3_name`, `state`, `mmm_code`, `year`, `quality_score` |
| `data/clean/access_sa3.csv` | `sa3_code`, `year`, `care_type`, `total_users` |
| `data/raw/population/` | `sa3_code`, `pop_65_plus` |
| `data/raw/geography/` | SA3 shapefile (GeoJSON or SHP from ABS) |

---

## How to compute care_gap_index

```python
# Step 1: access_rate — residential users as % of 65+ population
residential = access[access['care_type'] == 'Residential Care'][['sa3_code', 'year', 'total_users']]
residential = residential.rename(columns={'total_users': 'residential_users'})

df = residential.merge(pop[['sa3_code', 'pop_65_plus']], on='sa3_code')
df['access_rate'] = df['residential_users'] / df['pop_65_plus'] * 100

# Step 2: quality_score — average up from facility level to SA3 level
quality = (
    stars.groupby(['sa3_code', 'year'])['quality_score']
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
import folium
import streamlit_folium as sf

gdf = gpd.read_file('data/raw/geography/SA3_2021_AUST_GDA2020.shp')
gdf = gdf.rename(columns={'SA3_CODE21': 'sa3_code'})
gdf['sa3_code'] = gdf['sa3_code'].astype(str)
df['sa3_code']  = df['sa3_code'].astype(str)

gdf = gdf.merge(df[df['year'] == selected_year], on='sa3_code', how='left')

m = folium.Map(location=[-25, 133], zoom_start=4)
folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=['sa3_code', 'care_gap_index'],
    key_on='feature.properties.sa3_code',
    fill_color='YlOrRd',
    nan_fill_color='lightgrey',
    legend_name='Care Gap Index',
).add_to(m)
sf.st_folium(m, width=900)
```

---

## Key insights to surface

- Remote and Very Remote areas (MM5–MM7) have the highest care_gap_index
- Outer regional QLD, WA, NT stand out prominently
- Major cities have high user volumes but also higher quality — smaller gap
