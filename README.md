# DVN AT3 — Aged Care Quality & Access Gap (Australia)

A data journalism dashboard investigating where Australians aged 65+ face the largest gap between aged-care demand and quality-adjusted supply, joined at the SA3 level across three official sources.

## Core question
Which SA3 regions consistently combine high care demand (65+ population) with low Star-Rating-quality-adjusted bed supply, and what does that imply for families choosing care, health-system planners, and aged-care market entrants?

## Datasets
- ACQSC Aged Care Star Ratings (Feb 2025)
- People Using Aged Care — SA3 (Feb 2026)
- ABS Regional Population — 2024 ERP

Joined on `sa3_code` across 358 SA3 regions. Derived metrics: Access Rate, Composite Quality Score, Care Gap Index.

## Narrative arc
The Detective — start broad (national snapshot) → zoom in (state, MMM remoteness) → reveal the unexpected at the SA3 level.

## Dashboard
Streamlit + Plotly, four tabs: National Snapshot, The Trend, The Correlation, The Reveal.

## Dev commands
```
pip install -r requirements.txt
streamlit run dashboard/app.py
jupyter notebook notebooks/clean_pipeline/
```

## For Claude users
Project context, rules, and sub-agent profiles live in `.claude/`. Start by reading `CLAUDE.md` at the repo root.

## Team
MDSI 36103 Data Visual Narrative — Spring 2026 — Group of 7 (Andy, Alexandro, Fajar, Lavil, Rendra, Clarice, Dhiraj).
