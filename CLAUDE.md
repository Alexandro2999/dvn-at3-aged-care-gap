# DVN AT3 — Aged Care Quality & Access Gap (Australia)

## Project Overview

**Narrative arc:** The Detective — national overview → state comparison → SA3-level reveal

**Core question:** *Which Australian regions have the worst gap between aged care quality and access — and why?*

---

## Folder Structure

```
dvn-at3-aged-care-gap/
├── data/
│   ├── raw/
│   │   ├── star_ratings/                ← 12 quarterly Excel files (May 2023 → Feb 2026)
│   │   ├── service_list/                ← 7 annual service lists (2019–2025)
│   │   ├── admission/                   ← CURF admission records (2019–2024), individual-level
│   │   ├── service_users_CURF/          ← CURF individual-level service user records (2018–2024)
│   │   ├── service_users_snapshot_SA3/  ← GEN aggregated counts by SA3 (2023–2025)
│   │   ├── abs_population/              ← ABS SA3 population (total_pop, pop_65_plus)
│   │   └── abs_geography/               ← SA3 shapefile for choropleth
│   └── clean/                           ← pipeline outputs, never edit manually
│       ├── README.md                    ← full data dictionary for all output files
│       ├── star_ratings_by_facility.csv
│       ├── service_supply_by_sa3.csv
│       ├── service_users_by_sa3.csv
│       ├── homecare_admissions_by_acpr.csv
│       ├── home_care_users_by_acpr.csv
│       ├── residential_admissions_by_acpr.csv
│       ├── residential_users_by_acpr.csv
│       └── service_funding_by_facility.csv
├── notebooks/clean_pipeline/            ← run in order 01 → 06
├── notebooks/architect/                 ← dashboard notebooks
├── dashboard/                           ← Streamlit app
├── assets/                              ← charts, moodboard, palette
├── requirements.txt
└── CLAUDE.md
```

---

## Data Pipeline (`notebooks/clean_pipeline/`)

Run notebooks **in order**. Full column descriptions in `data/clean/README.md`.

### 01 — `01_treat_star_ratings.ipynb` → `star_ratings_by_facility.csv`
- **Source:** `data/raw/star_ratings/` (12 quarterly Excel files)
- **SA3 lookup:** multi-year fallback 2025 → 2024 → 2023 from `data/raw/service_list/`
- **Output:** one row per facility × quarter
- **Key columns:** `sa3_code`, `sa3_name`, `state`, `mmm_code`, `year`, `quarter`, `overall_rating`, `residents_exp`, `staffing`, `compliance`, `quality_measures`, `quality_score`
- **Note:** `quality_score = mean(residents_exp, staffing, compliance, quality_measures)`

### 02 — `02_treat_service_list.ipynb` → `service_supply_by_sa3.csv`
- **Source:** `data/raw/service_list/` (2019–2025)
- **Postcode→SA3 mapping:** two-tier: Tier 1 = unambiguous postcode, Tier 2 = postcode + ACPR tiebreaker
- **Output:** one row per SA3 × year (2019–2025)
- **Key columns:** `sa3_code`, `sa3_name`, `year`, `n_residential`, `n_homecare`, `residential_places`, `homecare_places`, `n_nfp`, `n_government`, `n_private`

### 03 — `03_treat_service_users_snapshots.ipynb` → `service_users_by_sa3.csv`
- **Source:** `data/raw/service_users_snapshot_SA3/` (GEN files, 2023–2025)
- **Output:** one row per SA3 × year, point-in-time as at 30 June
- **Key columns:** `sa3_code`, `sa3_name`, `year`, `permanent`, `respite`, `total_residential`, `hcp_level1`–`hcp_level4`, `total_homecare`, `hcp_high_needs`

### 04 — `04_treat_admissions_homecare.ipynb`
- **Part 1** → `homecare_admissions_by_acpr.csv` — from `data/raw/admission/`, home care only
- **Part 2** → `home_care_users_by_acpr.csv` — from `data/raw/service_users_CURF/`, home care only
- **Note:** ACPR level only — SA3 not available in CURF records

### 05 — `05_treat_residential.ipynb`
- **Part 1** → `residential_admissions_by_acpr.csv` — from `data/raw/admission/`, residential only
- **Part 2** → `residential_users_by_acpr.csv` — from `data/raw/service_users_CURF/`, residential only

### 06 — `06_treat_service_funding.ipynb` → `service_funding_by_facility.csv`
- **Source:** `data/raw/service_list/` funding column
- **Output:** one row per facility × year — service name, SA3, org type, funding
- **Note:** `org_type` = `profit` / `not_for_profit` / `government`. Negative = clawback, kept as-is.

---

## Metrics

### Core metrics (must have)

| Metric | Formula | Grain |
|--------|---------|-------|
| `quality_score` | mean(residents_exp, staffing, compliance, quality_measures) | facility × quarter |
| `access_rate` | total_residential / pop_65_plus × 100 | SA3 × year |
| `care_gap_index` | access_rate / quality_score | SA3 × year — headline metric |
| `hcp_high_needs` | hcp_level3 + hcp_level4 | SA3 × year |
| `beds_per_1000_elderly` | residential_places / pop_65_plus × 1000 | SA3 × year |

### Extended metrics (ideas to explore)

| Metric | Formula | Story it tells |
|--------|---------|----------------|
| `waitlist_pressure` | hcp_high_needs / residential_places | How many high-needs HCP users per residential bed — hidden demand |
| `desert_score` | 1 if n_residential = 0 AND pop_65_plus > threshold | Regions with elderly population but zero facilities |
| `supply_change` | n_residential_2025 - n_residential_2019 | Which SA3s are losing facilities |
| `private_share` | n_private / n_facilities | Market concentration by for-profit providers |
| `quality_trend_slope` | linear regression of quality_score over quarters | Is quality improving or declining per SA3 |
| `funding_per_bed` | total_funding / residential_places | Government investment efficiency |
| `quality_gap_by_org` | avg quality (nfp) - avg quality (profit) | Does ownership type predict quality |
| `mandate_effect` | quality delta pre/post Oct 2023 | Impact of staffing mandate |

---

## Story Angles

Multiple angles to explore — pick the strongest combination for the narrative:

### 1. "The Desert Map"
SA3 regions with zero residential facilities, especially those with growing 65+ populations.
66 SA3s lost at least one residential facility between 2023→2025.
**Visual:** Choropleth coloured by `desert_score` or `supply_change`

### 2. "The For-Profit Problem"
Private facilities concentrated in metro areas (high profit) while NFP/govt serve remote areas.
Private share ~30% nationally but their quality score distribution may differ.
**Visual:** Box plot quality by org type, map of private share by SA3

### 3. "The Mandate Effect"
October 2023 staffing mandate — did it actually improve star ratings?
Look for quality inflection point in the time series.
**Visual:** Line chart quality over time with Oct 2023 marked, before/after comparison by state

### 4. "The Waitlist Trap"
HCP Level 3+4 users (high needs) stuck at home because residential capacity is full or absent.
`waitlist_pressure` reveals where the bottleneck is worst.
**Visual:** Scatter access_rate vs hcp_high_needs, bubble size = pop_65_plus

### 5. "The Remote Penalty"
MMM remoteness vs both quality AND access — double disadvantage.
Remote regions have fewer facilities AND lower star ratings.
**Visual:** Choropleth + bar chart by MMM band

### 6. "The Demographic Story"
Indigenous and NESB users concentrated in regions with worst access.
Requires ACPR-level data (can't map to SA3 directly).
**Visual:** Bar chart n_indigenous / n_nesb by ACPR ranked by care_gap_index

### 7. "The Funding Story"
Does more government funding per bed translate to better quality?
Negative funding (clawback) concentrated in which org types / regions?
**Visual:** Scatter funding_per_bed vs quality_score, colour by org_type

### 8. "The Supply Collapse"
Residential supply growing slower than 65+ population — a slow-motion crisis.
`beds_per_1000_elderly` declining in most states.
**Visual:** Line chart beds_per_1000_elderly by state 2019→2025

---

## Visual Ideas

### Map visuals
- Choropleth: `care_gap_index` by SA3 — headline
- Choropleth: `supply_change` 2019→2025 — who is losing facilities
- Choropleth: `private_share` — market concentration
- Choropleth: `waitlist_pressure` — hidden demand
- Dot map: individual facility closures 2023→2025

### Time series
- Line: avg quality_score by state over quarters (mark Oct 2023 mandate)
- Line: beds_per_1000_elderly by state 2019→2025
- Area: total residential vs homecare users nationally 2023→2025
- Slope chart: quality rank of states before/after mandate

### Distributions & comparisons
- Box plot / violin: quality_score by org_type (profit vs NFP vs govt)
- Box plot: quality_score by MMM band
- Bar: care_gap_index top 20 worst SA3 regions
- Bar: n_indigenous / n_nesb in worst-access ACPR regions
- Histogram: distribution of care_gap_index nationally

### Relationships
- Scatter: access_rate vs quality_score (colour = MMM, size = pop_65_plus)
- Scatter: funding_per_bed vs quality_score (colour = org_type)
- Scatter: private_share vs quality_score by SA3
- Heatmap: state × year quality (see trends and outliers)

---

## Dashboard Features

### Filters
- State / territory
- Remoteness class (MMM1–MM7)
- Organisation type (profit / not_for_profit / government)
- Care type (residential / home care)
- Year

### Interactions
- Click SA3 on map → detail card (facility list, rating breakdown, org type, pop_65_plus)
- Toggle between metrics on choropleth
- Highlight SA3 in all charts simultaneously

### What-if
- Slider: "minimum beds per 1,000 elderly" → recolour map to show which SA3s fall below threshold
- Slider: "quality floor" → highlight facilities below threshold
- Toggle: show/hide facility closures 2019→2025 as overlay

---

## Geographic Units

| Unit | Count | Used for |
|------|-------|---------|
| SA3 | ~331–359 regions | Main join key — all dashboard visuals |
| ACPR | 73 regions | Demographics only (CURF data limitation) |
| MMM code | MM1–MM7 | Remoteness classification |
