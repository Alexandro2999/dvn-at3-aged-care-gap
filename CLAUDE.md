# DVN AT3 — Aged Care Quality & Access Gap (Australia)

## Project Overview

**Course:** Data Visual Narrative (DVN) — Assignment 3
**Group repo:** https://github.com/Alexandro2999/dvn-at3-aged-care-gap
**Miro board:** https://miro.com/app/board/uXjVGiNHprY=/
**Narrative arc:** The Detective — national overview → state comparison → SA3-level reveal

**Core question:** *Which Australian regions have the worst gap between aged care quality and access — and why?*

---

## Team

| Name | Role |
|------|------|
| Andy | Orator & Project Lead |
| Alexandro | Architect — dashboard/components |
| Fajar | Architect — dashboard/components |
| Dhiraj | Architect — dashboard/components |
| Lavil | Analyst — data/ + notebooks/analyst |
| Rendra | Artist — assets/ |

---

## Deadlines

| Part | What | Due |
|------|------|-----|
| Part 1 | Dataset pitch + OCEAN persona + Game Plan | Sun 19 Apr 2026 ✅ |
| Part 2 | Persuasion Pitch (in class, 10 min + Q&A) | Wed 13 May 2026 |
| Part 3 | Final Portfolio (live dashboard + video + data dict) | Sun 17 May 2026 |

---

## Folder Structure

```
dvn-at3-aged-care-gap/
├── data/
│   ├── raw/
│   │   ├── star_ratings/          ← 12 quarterly Excel files (May 2023 → Feb 2026)
│   │   ├── service_list/          ← 7 annual service lists (2019–2025), used for SA3 lookup
│   │   ├── admission/             ← CURF admission records (2019–2024), individual-level
│   │   ├── people_using_aged_care/← GEN aggregated counts (2018–2025)
│   │   ├── population/            ← ABS SA3 population (total_pop, pop_65_plus, MMM remoteness)
│   │   └── geography/             ← SA3 shapefile for choropleth
│   └── clean/                     ← pipeline outputs, never edit manually
│       ├── stars_timeline.csv
│       ├── supply_sa3.csv
│       ├── access_sa3.csv
│       └── demographics_acpr.csv
├── notebooks/analyst/             ← run in order 01 → 06
├── dashboard/components/          ← Streamlit app
├── assets/                        ← charts, moodboard, palette
├── requirements.txt
└── CLAUDE.md
```

---

## Data Pipeline (notebooks/analyst/)

Run notebooks **in order**. Each produces one clean file.

### 01 — Stars Pipeline → `stars_timeline.csv`
- **Source:** `data/raw/star_ratings/` (12 quarterly Excel files)
- **SA3 lookup:** multi-year fallback 2025 → 2024 → 2023 from `data/raw/service_list/`
- **Output:** 31,290 rows × 18 cols — one row per facility × quarter
- **Key columns:** `sa3_code`, `sa3_name`, `state`, `mmm_code`, `year`, `quarter`, `overall_rating`, `residents_exp`, `staffing`, `compliance`, `quality_measures`, `quality_score`
- **Note:** `quality_score = mean(residents_exp, staffing, compliance, quality_measures)`

### 02 — Supply Pipeline → `supply_sa3.csv`
- **Source:** `data/raw/service_list/` (2019–2025)
- **Postcode→SA3 mapping:** built internally from 2023–2025 files (two-tier: Tier 1 = unambiguous postcode, Tier 2 = postcode + ACPR tiebreaker)
- **Output:** 2,307 rows — one row per SA3 × year (2019–2025)
- **Key columns:** `sa3_code`, `sa3_name`, `year`, `n_residential`, `n_home_care`, `residential_places`, `home_care_places`

### 03 — Access Pipeline → `access_sa3.csv`
- **Source:** `data/raw/people_using_aged_care/` (GEN files, 2023–2025 only)
- **Output:** 1,005 rows — one row per SA3 × year × care_type
- **Key columns:** `sa3_code`, `sa3_name`, `year`, `care_type`, `total_users`, `hcp_high_needs` (Level 3+4, proxy for residential waitlist)

### 04 — Demographics Pipeline → `demographics_acpr.csv`
- **Source:** BOTH `data/raw/admission/` (2019–2024) AND `data/raw/people_using_aged_care/` (2018–2024)
- **Geography:** ACPR level (73 regions) — SA3 not available in CURFs
- **Output:** one row per ACPR × year × care_type × source
- **Key columns:**
  - `total_users` — from people_using files (stock of current users)
  - `n_first_admission`, `pct_first_admission` — new entrants / total_users (from people_using)
  - `pct_nesb` — % born in non-English-speaking country
  - `pct_indigenous` — % Aboriginal or Torres Strait Islander
  - `pct_female`
  - `hcp_l1`, `hcp_l2`, `hcp_l3`, `hcp_l4` — raw counts per HCP level (Home Care only)
- **Note:** `source = 'admission'` has richer demographics; `source = 'people_using'` has broader coverage

### 05 — Story EDA → charts in `assets/`
- Explores care_gap_index distribution, staffing mandate Oct 2023 turning point, NESB/remote patterns
- Charts saved as PNG for use in dashboard and presentation

---

## Key Metrics

| Metric | Formula | Grain |
|--------|---------|-------|
| `quality_score` | mean(residents_exp, staffing, compliance, quality_measures) | facility × quarter |
| `access_rate` | residential_users / pop_65_plus × 100 | SA3 × year |
| `care_gap_index` | access_rate / quality_score | SA3 × year — headline metric |
| `pct_first_admission` | n_first_admission / total_people_using | ACPR × year |
| `hcp_high_needs` | Level 3 + Level 4 users | SA3 × year |

---

## Geographic Units

| Unit | Count | Used for |
|------|-------|---------|
| SA3 | ~358 regions | Main join key — all dashboard visuals |
| ACPR | 73 regions | Demographics only (CURF data limitation) |
| MMM code | MM1–MM7 | Remoteness classification (from star ratings service list) |

---

## 4 Planned Visuals

| # | Type | Key metric | Purpose |
|---|------|-----------|---------|
| V1 | Choropleth map | `care_gap_index` | Where is the problem? |
| V2 | Scatter plot | `access_rate` vs `quality_score` | Do more users = worse quality? |
| V3 | Ranked bar | `care_gap_index` top/bottom 20 SA3 | These are the worst regions |
| V4 | Line / area | Avg star rating over time by state | Is it getting better? (Oct 2023 mandate) |

---

## 3 Advanced Features

- **Context-Aware Filtering:** state, remoteness class, rating tier dropdowns — all visuals update together
- **Visual Tooltips / Modals:** click SA3 on map → detail card (facility list, rating breakdown, pop_65_plus)
- **What-If Parameterisation:** slider "minimum beds per 1,000 elderly" → recolour map live
