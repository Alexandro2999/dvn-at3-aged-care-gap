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

🟡 **Phase 1: Story & Insights** — active  
⬜ **Phase 2: Dashboard** — blocked until Phase 1 complete

Phase 2 command: `.claude/commands/phase2/dashboard.md` (inactive — move to `.claude/commands/` when Phase 2 begins)

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
│   ├── clean_pipeline/                  ← run in order 01 → 07
│   └── architect/                       ← EDA + metrics (01_eda, 02_metrics)
├── dashboard/                           ← Streamlit app (app.py)
├── assets/                              ← charts, moodboard, palette
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

## Detail References

- Pipeline + extended metrics + geo: `.claude/rules/data.md`
- Story angles + narrative rules: `.claude/rules/narrative.md`
- Dashboard visuals + features (Phase 2): `.claude/rules/dashboard.md`
