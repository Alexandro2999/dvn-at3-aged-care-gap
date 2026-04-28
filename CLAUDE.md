# DVN AT3 — Aged Care Quality & Access Gap (Australia)

## Project Overview

**Course:** Data Visual Narrative (DVN) — Assignment 3  
**Group repo:** https://github.com/Alexandro2999/dvn-at3-aged-care-gap  
**Miro board:** https://miro.com/app/board/uXjVGiNHprY=/  
**Andy's role:** Orator & Project Lead  
**Narrative arc:** The Detective — guide the viewer from national overview → state comparison → SA3-level reveal

---

## The Core Question

> *Which Australian regions have the worst gap between aged care quality and access — and why?*

The dashboard should feel like a detective story: each visual adds a new clue until the worst-served communities are exposed.

---

## Datasets (all files go in `data/raw/`)

| File | Source | Key columns |
|------|--------|-------------|
| `star_ratings_feb2025.csv` | [gen-agedcaredata.gov.au](https://www.gen-agedcaredata.gov.au/resources/access-data/2025/february/star-ratings) | facility_id, SA3_code, SA3_name, overall_rating, residents_exp, staffing, compliance, quality_measures |
| `people_using_aged_care_feb2026.csv` | [gen-agedcaredata.gov.au](https://www.gen-agedcaredata.gov.au/resources/access-data/2026/february/people-using-aged-care) | SA3_code, SA3_name, state, total_users, home_care_users, residential_users |
| `abs_regional_population_sa3_2024.csv` | [abs.gov.au](https://www.abs.gov.au/statistics/people/population/regional-population/2022-23) | SA3_code, SA3_name, state, total_pop, pop_65_plus, remoteness_class |

**Join key:** `SA3_code` — consistent across all three files (~358 regions)

---

## Derived Metrics to Engineer (in `data/clean/`)

```python
# Access Rate — how many elderly residents are actually using care
access_rate = people_using / pop_65_plus * 100  # per SA3

# Quality Score — weighted average of Star Rating sub-dimensions
quality_score = weighted_mean([residents_exp, staffing, compliance, quality_measures])

# Care Gap Index — demand vs supply pressure
care_gap_index = access_rate / quality_score  # higher = more underserved

# Remoteness — already in ABS data as ARIA+ class (Major City / Inner Regional / Outer Regional / Remote / Very Remote)
```

---

## Data Exploration Goals

When exploring the data, focus on these questions in order:

1. **Shape check** — how many rows per dataset? Any SA3 codes missing across files? Any nulls in key columns?
2. **Join feasibility** — do SA3 codes match format exactly? Need zero-padding or string cleanup?
3. **Distribution** — what does the spread of Star Ratings look like? Are low ratings concentrated in certain states or remoteness classes?
4. **Correlation** — does high access rate correlate with lower quality? (scatter: access_rate vs quality_score)
5. **Outliers** — which SA3 regions are most extreme on Care Gap Index?
6. **Temporal** — if multiple time periods available, is quality improving or declining per region?

---

## 4 Planned Visuals

| # | Chart type | X | Y | Colour/Size | Purpose |
|---|-----------|---|---|-------------|---------|
| V1 | Choropleth map | SA3 geography | — | Care Gap Index | Spatial overview — "where is the problem?" |
| V2 | Scatter plot | Access Rate | Quality Score | Size = pop_65_plus | Correlation — "do more users = worse quality?" |
| V3 | Ranked bar | SA3 name | Care Gap Index | Top/Bottom 20 | Detective reveal — "these are the worst regions" |
| V4 | Line / area | Time period | Avg Star Rating | Colour = state | Trend — "is it getting better or worse?" |

---

## 3 Advanced Features

- **Context-Aware Filtering:** dropdowns for state, remoteness class, rating tier — all visuals update together
- **Visual Tooltips / Modals:** click SA3 on map → detail card (facility list, rating breakdown, 65+ pop)
- **What-If Parameterisation:** slider "minimum beds per 1,000 elderly" → recolour map live

---

## Folder Structure

```
dvn-at3-aged-care-gap/
├── data/
│   ├── raw/              ← original CSVs, never modify
│   └── clean/            ← joined & engineered data
├── notebooks/
│   └── analyst/          ← Andy's EDA notebooks go here
├── dashboard/
│   └── components/       ← Streamlit app (Architects)
├── assets/               ← moodboard, palette (Artist)
├── requirements.txt
└── CLAUDE.md             ← you are here
```

---

## Suggested EDA Starting Commands

```python
import pandas as pd

# Load
stars  = pd.read_csv("data/raw/star_ratings_feb2025.csv")
people = pd.read_csv("data/raw/people_using_aged_care_feb2026.csv")
pop    = pd.read_csv("data/raw/abs_regional_population_sa3_2024.csv")

# Shape
print(stars.shape, people.shape, pop.shape)

# Check SA3 join key
print("Stars SA3 unique:", stars["SA3_code"].nunique())
print("People SA3 unique:", people["SA3_code"].nunique())
print("Pop SA3 unique:", pop["SA3_code"].nunique())

# Merge
df = stars.merge(people, on="SA3_code").merge(pop, on="SA3_code")
print("Merged shape:", df.shape)

# Engineer metrics
df["access_rate"]    = df["total_users"] / df["pop_65_plus"] * 100
df["quality_score"]  = df[["residents_exp","staffing","compliance","quality_measures"]].mean(axis=1)
df["care_gap_index"] = df["access_rate"] / df["quality_score"]

# Quick look
df[["SA3_name","state","access_rate","quality_score","care_gap_index"]].sort_values("care_gap_index", ascending=False).head(20)
```

---

## Key Contacts

| Name | Role | GitHub area |
|------|------|-------------|
| Andy (me) | Orator & Project Lead | narrative docs (Miro/Drive) |
| Alexandro | Architect | dashboard/components |
| Fajar | Architect | dashboard/components |
| Dhiraj | Architect | dashboard/components |
| Lavil | Analyst | data/ + notebooks/analyst |
| Rendra | Artist | assets/ |

---

## Part Deadlines

| Part | What | Due |
|------|------|-----|
| Part 1 | Dataset pitch + OCEAN persona + Game Plan | Sun 19 Apr 2026 ✅ |
| Part 2 | Persuasion Pitch (in class, 10 min + Q&A) | Wed 13 May 2026 |
| Part 3 | Final Portfolio (live dashboard + video + data dict) | Sun 17 May 2026 |
