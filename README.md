# DVN AT3 — Australia's Aged Care Gap

A data journalism dashboard investigating which Australian SA3 regions face the largest gap between aged-care demand and quality-adjusted supply.

**Core question:** Which communities combine high 65+ care demand with low Star-Rating-quality-adjusted bed supply — and why?

**Narrative arc:** The Detective — national overview → state / remoteness comparison → SA3-level reveal.

**Course:** MDSI 36103 Data Visual Narrative — Autumn 2026 — UTS

---

## 🔗 Deliverables

| Artefact | Link |
|---|---|
| 🖥️ Live dashboard (Streamlit Cloud) | _pending — to be published before submission_ |
| 🎬 Video walkthrough (3 min) | https://www.youtube.com/watch?v=x1xw13D1Qh0 |
| 📊 Source repository | https://github.com/Alexandro2999/dvn-at3-aged-care-gap |
| 📒 Data dictionary | [data/clean/README.md](data/clean/README.md) |
| 🎯 Interactive features | See _Advanced Features_ section below |

---

## 🎯 Advanced Features

The dashboard implements **all four** of the rubric's advanced features. Each is also surfaced in the in-app Methodology page so markers can find them without reading source.

| Feature | Where to see it | What changes |
|---|---|---|
| **Context-Aware Filtering** | Sidebar State + MMM picker (every chapter) | All chapter charts and narrative callouts recompute against the active scope |
| **Click-to-Drill (Tooltip/Modal)** | Ch 3 — bar of worst-pressure SA3s | Clicking a bar updates the HCP-level (L1–L4) donut beside it |
| **Narrative Scrollytelling** | 4-chapter detective arc | Breadcrumb + chapter-closer scaffolding guide the reader Gap → Cause → Victims → Verdict |
| **What-If Parameterisation** | Ch 4 — What-if tab | RN-minutes-target slider recomputes compliant-facility counts and pass/fail callout live |

---

## Team

**Lead author & primary build:** Andy Pham (Quan) — clean data pipeline, three of the four chapter analyses, the dashboard polish from prototype → submission-ready (chapter narrative scaffolding, Methodology page, advanced-features wiring, README + repo cleanup).

| Name | Role / Key contributions |
|---|---|
| **Andy Pham (Quan)** _(lead)_ | Full clean pipeline (all 7 notebooks); Chapter 1, 3, and 4 analyses (mandate effect, waitlist-divergence, supply-collapse visuals); dashboard polish — chapter scaffolding, Methodology page, click-drill + What-if features, palette + accessibility passes; story/insight assets; README, repo hygiene, PRs / CI |
| **Alexandro Sianipar** | Repo init & folder scaffold; architect notebooks (`01_eda`, `02_metrics`, `master_sa3`); Ch3 notebook draft; Ch1 chart label fixes; home-page legend clarity |
| **Fajar (Facholhidayat)** | Chapter 2 analysis notebook; map rendering & GeoJSON deployment; dashboard cosmetics; Ch1 & Ch2 visualisation refinements |
| **Rendra Hutama** | Basic EDA notebook; Streamlit dashboard design; dashboard iteration from Andy's presentation |
| **Lavil** | Contributing analysis (Ch2–Ch3 scope) |
| **Clarice** | Contributing analysis |
| **Dhiraj** | Contributing analysis |

---

## Directory Structure

```
dvn-at3-aged-care-gap/
│
├── data/
│   ├── raw/                              ← source files — never edit
│   │   ├── star_ratings/                 ← 12 quarterly XLSX snapshots (May 2023 → Feb 2026)
│   │   ├── service_list/                 ← 7 annual service-list snapshots (2019–2025)
│   │   ├── admission/                    ← CURF admission records (homecare + residential)
│   │   ├── service_users_CURF/           ← individual-level CURF service-user records
│   │   ├── service_users_snapshot_SA3/   ← GEN aggregated counts by SA3 (2023–2025)
│   │   ├── abs_population/               ← ABS SA3 population (total_pop, pop_65_plus)
│   │   └── abs_geography/                ← SA3 shapefile + simplified GeoJSON for choropleth
│   │
│   └── clean/                            ← pipeline outputs — never edit manually
│       ├── master_sa3.csv                ← single dashboard source (SA3 × year, all metrics)
│       ├── star_ratings_by_facility.csv
│       ├── service_supply_by_sa3.csv
│       ├── service_users_by_sa3.csv
│       ├── service_funding_by_facility.csv
│       ├── abs_population_by_sa3.csv
│       ├── residential_users_by_acpr.csv
│       ├── home_care_users_by_acpr.csv
│       └── ...
│
├── notebooks/
│   ├── clean_pipeline/                   ← run 01 → 07 in order to rebuild data/clean/
│   │   ├── 01_treat_star_ratings.ipynb
│   │   ├── 02_treat_service_list.ipynb
│   │   ├── 03_treat_service_users_snapshots.ipynb
│   │   ├── 04_treat_admissions_homecare.ipynb
│   │   ├── 05_treat_residential.ipynb
│   │   ├── 06_treat_service_funding.ipynb
│   │   └── 07_treat_abs_population.ipynb
│   │
│   ├── architect/                        ← EDA and master_sa3 builder
│   │   ├── 01_eda.ipynb                  ← national overview, quality over time, for-profit gap
│   │   └── 02_metrics.ipynb              ← joins all clean CSVs → master_sa3.csv
│   │
│   ├── artist/                           ← UI/UX design assets
│   │   ├── DVN AT3 Design.pdf            ← full design spec
│   │   ├── Color Pallete.png             ← colour palette reference
│   │   ├── Landing Page.png              ← landing page wireframe
│   │   ├── Chapter 1_ The Map.png        ← chapter wireframes (Ch1–Ch4)
│   │   ├── Chapter 2_ The Correlation.png
│   │   ├── Chapter 3_ The Reveal.png
│   │   ├── Chapter 4_ Mandate Effect.png
│   │   └── assets/                       ← production assets used by the dashboard
│   │       ├── ico-dashboard.png         ← sidebar icon
│   │       └── img-landing-bg.jpg        ← Home hero background image
│   │
│   └── analyst/                          ← one notebook per chapter
│       ├── 01_chapter_the_map.ipynb
│       ├── 02_chapter_the_correlation.ipynb
│       ├── 03_chapter_the_reveal.ipynb
│       └── 04_chapter_mandate_effect.ipynb
│
├── dashboard/                            ← Streamlit app
│   ├── app.py                            ← entry point — loads data, routing, global CSS/nav
│   └── tabs/
│       ├── home.py                       ← Home page
│       ├── ch1_map.py                    ← Chapter 1: The Gap
│       ├── ch2_correlation.py            ← Chapter 2: The Cause
│       ├── ch3_reveal.py                 ← Chapter 3: The Victims
│       ├── ch4_mandate.py                ← Chapter 4: The Verdict
│       ├── methodology.py                ← About page: data sources, formulas, caveats, advanced-features legend
│       ├── fullmap.py                    ← interactive choropleth (embedded in Home + Ch1)
│       └── utils.py                      ← shared constants, colour palettes, theme helper
│
├── assets/                               ← chapter insight markdown files
│   ├── chapter_01_the_map.md
│   ├── chapter_02_the_correlation.md
│   ├── chapter_03_the_reveal.md
│   └── chapter_04_mandate_effect.md
│
├── slides_deck/                          ← Part 2 pitch deliverable
│   └── Australias-Aged-Care-Gap.pptx     ← final deck
│
├── requirements.txt
└── README.md
```

---

## How to Run the Dashboard

**Stack:** Python 3 · Streamlit · Plotly · Pandas · GeoPandas (clean pipeline) · Jupyter.

```bash
# 1. Install dependencies (use a virtual environment)
pip install -r requirements.txt

# 2. Run from inside the dashboard/ directory
cd dashboard
streamlit run app.py
```

The app opens at `http://localhost:8501`. The sidebar provides global State / Remoteness (MMM) filters that propagate to all chapters.

> **Note:** `sa3_simplified.geojson` is fetched automatically from GitHub on first run if it is not present locally. Subsequent runs use the cached file.

### Rebuild clean data (optional)

```bash
jupyter notebook notebooks/clean_pipeline/
# Run notebooks 01 → 07 in order
```

---

## Core Metrics

| Metric | Formula | Grain |
|---|---|---|
| `quality_score` | mean(residents_exp, staffing, compliance, quality_measures) | facility × quarter |
| `access_rate` | total_residential / pop_65_plus × 100 | SA3 × year |
| `care_gap_index` | access_rate / quality_score | SA3 × year — headline metric |
| `hcp_high_needs` | hcp_level3 + hcp_level4 | SA3 × year |
| `waitlist_pressure` | hcp_high_needs / residential_places | SA3 × year |
| `beds_per_1000_elderly` | residential_places / pop_65_plus × 1000 | SA3 × year |

---

## 📒 Data Dictionary

Per-CSV column definitions, types, and provenance live in [data/clean/README.md](data/clean/README.md) — one section per file produced by the clean pipeline (`notebooks/clean_pipeline/01` → `07`). Open that file for grain, formulas, and source-system notes for every column the dashboard loads.

---

## Dashboard Content — Page by Page

### Home (`?page=home`)

Hero banner with project tagline and 2025 outlook note.

**Interactive Map tab** — full-page choropleth (see fullmap below) with metric selector and 2025 forecast toggle.

**Find My Area tab** — SA3 search box:
- Crisis-zone warning if `waitlist_pressure > 1.0`
- Three KPI cards: Care Gap Index, Quality Score, Access Rate (each vs national and state average)
- Mini trend line charts for all three metrics (2023–2025)
- Top-5 facilities table by quality score, filterable by ownership type (For Profit / Not for Profit / Government)

---

### Chapter 1 — The Gap (`?page=map`)
*"Where do the patterns live?"*

**Snapshot tab**
- Year toggle (2023 / 2024)
- Three KPI cards: Avg Care Gap Index, Avg Quality Score, Avg Residential Access
- Insight callout: top-10 worst SA3s by care gap (highlights if all are MM1 major-city)
- View toggle — By State or By Remoteness (MMM):
  - Three side-by-side horizontal bar charts: Care Gap Index · Quality Score · Access Rate
- SA3 Rankings section: configurable Top-N slider, metric selector, Worst/Best direction — horizontal bar chart

**Trend tab**
- View toggle — By State or By MMM
- Two line charts showing % change from 2019: Beds per 1,000 elderly and Number of Facilities
- Auto-generated callout: which states/bands lost the most beds, national decline %

---

### Chapter 2 — The Cause (`?page=correlation`)
*"Who runs the best facilities?"*

Four KPI cards: Government / Non-Profit / For-Profit average quality scores, Ownership Gap (pts).

**Quality tab**
- Grouped bar chart: sub-rating breakdown (Residents Exp., Staffing, Compliance, Quality Measures) by ownership type across all snapshots
- Callout: staffing drives the full ownership gap; clinical outcomes nearly identical across ownership

**Funding tab**
- KPI cards: Total Funding latest year, Funding Ratio (for-profit ÷ government per facility), For-Profit Funding total
- Toggle: Per facility ($M) or Per bed ($k)
- Horizontal bar chart — funding per facility/bed by ownership
- Donut pie — funding share by ownership, year selector
- Callout: for-profit receives more public funding per unit yet delivers lower staffing ratings

**Together tab**
- National benchmark warning: funding ratio vs staffing gap vs identical clinical outcomes
- Toggle: scatter X-axis as funding per bed ($k) or per facility ($M)
- SA3-level scatter: funding vs quality score, bubble size = residential places, colour = private-facility share %
- Callout: correlation coefficient and average funding; ownership matters more than spend

---

### Chapter 3 — The Victims (`?page=reveal`)
*"Which communities are being left behind?"*

Headline: L4 (very-high needs) HCP cohort growth warning.

**Crisis zones over time**
- KPI cards: count of SA3 crisis zones (waitlist_pressure > 1.0) per year with net change delta
- Entry/exit callout: how many SA3s entered and resolved deficit year-on-year

**Which SA3s? (interactive drill)**
- Year toggle, Worst/Best direction, Top-N slider
- Horizontal bar chart of SA3s by Waitlist Pressure Index (red = top quartile)
- Click any bar → HCP-level donut (L1–L4 mix) and total home-care user count update for that SA3

**Are beds flowing to where demand is?**
- Line chart: % change in residential beds from 2019, Crisis Zones vs Rest of Australia
- Callout: new beds flow toward regions already adequately supplied — misallocation, not shortage

---

### Chapter 4 — The Verdict (`?page=mandate`)
*"Did the Oct 2023 staffing mandate work?"*

Headline para: national quality delta pre/post mandate, staffing sub-rating jump, flat clinical outcomes.
Ownership-gap recap linking back to Chapter 2.

**Timeline tab**
- KPI cards: Quality Δ post-mandate, Staffing Δ, Quality Measures Δ, Compliance % (latest)
- Line chart: national average quality score over time with Oct 2023 mandate vline
- Grouped bar: sub-rating before vs after mandate (Residents Exp., Staffing, Compliance, Quality Measures)
- Callout: mandate fixed inputs, not clinical outcomes

**By Owner tab**
- KPI cards: Government Compliance %, For-Profit Compliance %, Compliance Gap (pts)
- Line chart: quality by ownership over time with mandate vline
- Line chart: % of facilities fully compliant with staffing-minutes mandate by ownership
- Slope chart: state quality pre vs post mandate (top mover highlighted)
- Callout: same federal rule, opposite compliance outcomes by ownership type

**What-if tab**
- Slider: hypothetical RN-minutes target (0–250 min/day, current mandate = 44)
- KPI cards: facilities compliant, facilities below target, sector median actual
- Histogram: distribution of facility RN minutes with threshold vline and mandate reference
- Pass/fail callout vs 65% policy target

---

## Notebook Details — Roles & Content

### `notebooks/clean_pipeline/`

Run in order (01 → 07) to regenerate all `data/clean/` files.

| Notebook | Output | Description |
|---|---|---|
| `01_treat_star_ratings` | `star_ratings_by_facility.csv` | Combines 12 quarterly XLSX Star Rating snapshots; enriches with SA3 codes via service list join |
| `02_treat_service_list` | `service_supply_by_sa3.csv` | Counts facilities and licensed places per SA3 × year (2019–2025); org-type breakdown |
| `03_treat_service_users_snapshots` | `service_users_by_sa3.csv` | Counts people using aged care per SA3 × year; HCP levels L1–L4; demand-side data |
| `04_treat_admissions_homecare` | `homecare_admissions_by_acpr.csv` | Home care first/repeat admissions by ACPR × year from CURF admission records |
| `05_treat_residential` | `residential_admissions_by_acpr.csv`, `residential_users_by_acpr.csv` | Residential care admissions and snapshot users from CURF data |
| `06_treat_service_funding` | `service_funding_by_facility.csv` | Australian Government funding per facility × year from service list |
| `07_treat_abs_population` | `abs_population_by_sa3.csv` | ABS SA3 population by year; derives `total_pop` and `pop_65_plus` from 5-year age bands |

**Primary contributor:** Andy Pham (Quan) — full pipeline build and maintenance; Alexandro Sianipar — Ch1/Ch3 data fixes.

---

### `notebooks/architect/`

| Notebook | Output | Description |
|---|---|---|
| `01_eda.ipynb` | — | National EDA: quality over time, for-profit gap, remote penalty, supply decline, HCP waitlist pressure |
| `02_metrics.ipynb` | `master_sa3.csv` | Joins all five SA3-level clean files; computes 8 derived metrics (Care Gap Index, Access Rate, Waitlist Pressure, etc.) |

**Primary contributor:** Alexandro Sianipar and Fajar Hidayat

---

### `notebooks/artist/`

UI/UX design assets — no code, but feeds the dashboard's visual identity.

| File | Description |
|---|---|
| `DVN AT3 Design.pdf` | Full design specification: layout, colour system, typography |
| `Color Pallete.png` | Colour palette reference (navy, teal, gold, cream, care-gap red) |
| `Landing Page.png` | Home page wireframe |
| `Chapter 1–4 *.png` | Per-chapter layout wireframes |
| `assets/ico-dashboard.png` | Sidebar icon loaded by `app.py` |
| `assets/img-landing-bg.jpg` | Hero background image on the Home page |

**Primary contributor:** Rendra Budi Hutama

---

### `notebooks/analyst/`

| Notebook | Chapter | Description |
|---|---|---|
| `01_chapter_the_map.ipynb` | Ch 1 — The Gap | National care gap distribution; top-20 worst SA3s; state and MMM pattern charts |
| `02_chapter_the_correlation.ipynb` | Ch 2 — The Cause | Ownership quality gap; sub-rating breakdown; for-profit vs government scatter analysis |
| `03_chapter_the_reveal.ipynb` | Ch 3 — The Victims | Waitlist pressure SA3 ranking; HCP-level mix; crisis-zone vs rest-of-Australia bed supply |
| `04_chapter_mandate_effect.ipynb` | Ch 4 — The Verdict | Oct 2023 mandate effect; pre/post quality deltas; compliance by ownership |

**Contributors:** Andy Pham (Quan) — Ch1 supply visuals, Ch3 waitlist divergence, Ch4 mandate; Fajar (Facholhidayat) — Ch2 analysis; Alexandro Sianipar — Ch3 draft.
---

## Datasets

| Source | Files | Coverage |
|---|---|---|
| ACQSC Aged Care Star Ratings | `data/raw/star_ratings/` | 12 quarterly snapshots, May 2023 – Feb 2026 |
| ACQSC Service List | `data/raw/service_list/` | 7 annual snapshots, 2019–2025 |
| AIHW People Using Aged Care (SA3) | `data/raw/service_users_snapshot_SA3/` | 2023–2025 |
| AIHW CURF Admission Records | `data/raw/admission/`, `data/raw/service_users_CURF/` | 2018–2024 |
| ABS Regional Population | `data/raw/abs_population/` | SA3 level, 2001–2024 |
| ABS SA3 Geography | `data/raw/abs_geography/` | Shapefile + simplified GeoJSON |

Joined on `sa3_code` across 358 SA3 regions.
