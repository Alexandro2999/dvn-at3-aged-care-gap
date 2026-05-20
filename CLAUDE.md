# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# DVN AT3 — Aged Care Gap (Australia)

## Development Commands

```bash
# Install dependencies (use a venv)
pip install -r requirements.txt

# Run the dashboard (must run from inside dashboard/)
cd dashboard && streamlit run app.py

# Run clean pipeline — execute notebooks 01 → 07 in order
jupyter notebook notebooks/clean_pipeline/

```

---

## Project

**Core question:** *Which Australian regions have the worst gap between aged care quality and access — and why?*  
**Narrative arc:** The Detective — national overview → state comparison → SA3-level reveal

---

## Current Phase

✅ **Phase 1: Story & Insights** — done (4 chapter assets verified, all numbers traced to source)
✅ **Phase 2: Dashboard build** — done (5 chapters in `dashboard/app.py`)
✅ **Part 2: Pitch slides** — shipped 2026-05-12 (`slides_deck/Australias-Aged-Care-Gap.pptx` + `slides_deck/pitch_master.md`)
🟡 **Part 3: Final Portfolio polish** — ACTIVE · due Sun 17 May 2026

Part 3 critical path (5 days):
1. Verify 4 advanced features end-to-end (filtering, click-drill, scrollytelling, what-if sliders) — pitch S9 publicly promises these
2. Deploy to Streamlit Cloud
3. Record 3-min video walkthrough showcasing the 4 features
4. Polish data dictionary (`data/clean/README.md`) + annotate `dashboard/tabs/*.py`

Reference: `slides_deck/pitch_master.md` Part C has the full dashboard gap analysis.

---

## Folder Structure

```
dvn-at3-aged-care-gap/
├── data/
│   ├── raw/                             ← source files, never edit
│   │   ├── star_ratings/                ← 12 quarterly Excel files (May 2023 → Feb 2026)
│   │   ├── service_list/                ← 7 annual service lists (2019–2025)
│   │   ├── admission/                   ← CURF admission records (individual-level)
│   │   ├── service_users_CURF/          ← CURF individual-level service user records
│   │   ├── service_users_snapshot_SA3/  ← GEN aggregated counts by SA3 (2023–2025)
│   │   ├── abs_population/              ← ABS SA3 population (total_pop, pop_65_plus)
│   │   └── abs_geography/               ← SA3 shapefile for choropleth
│   └── clean/                           ← pipeline outputs, never edit manually
├── notebooks/
│   ├── clean_pipeline/                  ← 01 → 07, produces data/clean/
│   ├── architect/                       ← EDA + master_sa3.csv builder
│   └── analyst/                         ← one notebook per chapter
│       ├── 01_chapter_the_map.ipynb
│       ├── 02_chapter_the_correlation.ipynb
│       ├── 03_chapter_the_reveal.ipynb
│       └── 04_chapter_mandate_effect.ipynb
├── dashboard/                           ← Streamlit app (5 chapter tabs)
│   ├── app.py
│   └── tabs/                            ← home, ch1_map, ch2_correlation, ch3_reveal, ch4_mandate, fullmap, utils
├── assets/                              ← chapter insight files (English only)
│   ├── chapter_01_the_map.md
│   ├── chapter_02_the_correlation.md
│   ├── chapter_03_the_reveal.md
│   └── chapter_04_mandate_effect.md
├── slides_deck/                         ← Part 2 pitch deliverable
│   ├── Australias-Aged-Care-Gap.pptx    ← final deck
│   ├── pitch_master.md                  ← scripts + 52/52 data audit + Q&A + dashboard checklist
│   ├── slide_storyboard.html            ← layout reference for Part 3 video
│   ├── visual_for_slides.ipynb          ← chart PNG generator
│   └── assets/                          ← 7 chart PNGs (S3, S4, S5, S6, S7, S8, S11)
└── requirements.txt
```

---

## Core Metrics

| Metric | Formula | Grain |
|--------|---------|-------|
| `quality_score` | mean(residents_exp, staffing, compliance, quality_measures) | facility × quarter |
| `access_rate` | total_residential / pop_65_plus × 100 | SA3 × year |
| `care_gap_index` | access_rate / quality_score | SA3 × year — headline |
| `hcp_high_needs` | hcp_level3 + hcp_level4 | SA3 × year |
| `beds_per_1000_elderly` | residential_places / pop_65_plus × 1000 | SA3 × year |

---

## Core Chapters

| Chapter | Asset | Notebook | Dashboard tab | Status |
|---------|-------|----------|---------------|--------|
| Ch 1 — The Map | `chapter_01_the_map.md` | `01_chapter_the_map.ipynb` | `tabs/ch1_map.py` + `tabs/fullmap.py` | ✅ done |
| Ch 2 — The Correlation | `chapter_02_the_correlation.md` | `02_chapter_the_correlation.ipynb` | `tabs/ch2_correlation.py` | ✅ done |
| Ch 3 — The Reveal | `chapter_03_the_reveal.md` | `03_chapter_the_reveal.ipynb` | `tabs/ch3_reveal.py` | ✅ done |
| Ch 4 — Mandate Effect | `chapter_04_mandate_effect.md` | `04_chapter_mandate_effect.ipynb` | `tabs/ch4_mandate.py` | ✅ done |

Earlier "story angle" notebooks (For-Profit, Waitlist, Supply Collapse) were merged into Ch 2 / Ch 3 themes rather than created as separate notebooks. The 4-chapter dashboard structure is the canonical narrative now.

---

## Detail References

- Pipeline + extended metrics + geo: `.claude/rules/data.md`
- Narrative rules + audience tones: `.claude/rules/narrative.md`
- Dashboard visuals + advanced features rules: `.claude/rules/dashboard.md`
- External research citations (for callouts): `.claude/rules/external_research.md`
- Pitch deck source of truth: `slides_deck/pitch_master.md`
