# Chapter 2 — The Correlation: Who runs the best facilities?

## Narrative purpose

After seeing the map, the viewer asks: "Why is quality so different across regions?" This chapter gives the answer most people don't expect — it's not about location, it's about who owns the facility. Government and not-for-profit facilities consistently outperform private ones across every geography and every year in the dataset. The geography story is really an ownership story.

**Narrative arc:** The Detective — the Chapter 1 map left a crime scene (patches of low quality in major cities). Chapter 2 finds the culprit: ownership type, not location.

---

## Opening question by audience

| Audience | Their question |
|----------|---------------|
| **Families** | Is the facility near my parents government-run or private — and does it matter? |
| **Workers entering the sector** | Which type of employer actually invests in staff? |
| **Investors / businesses** | Where is the market underperforming relative to the funding it receives? |

---

## Key insights (all numbers confirmed from notebook run)

### Insight 1 — The ownership gap is 0.57 stars and has not moved
Government-run facilities average **4.07 stars** vs for-profit **3.50** — a gap of **0.57 points** across all 12 quarterly snapshots from May 2023 to February 2026. `[data — star_ratings_by_facility.csv, all snapshots 2023–2026]` The October 2023 staffing mandate lifted all ownership types, but did not compress the gap between them. It has been stable for three years.

**External validation:** Chu et al., JAMDA 2024 (2,476 facilities) — for-profit facilities are **8× less likely** to achieve 4–5 stars than government-run (OR 0.12, 95% CI 0.07–0.22). `[external — Chu et al., JAMDA 2024]`

> **Dashboard callout (warning):** For-profit: 3.50 stars. Government: 4.07 stars. A gap of 0.57 points — stable across every quarter since May 2023.

---

### Insight 2 — Staffing drives the entire gap; clinical outcomes do not
Breaking the composite quality score into 4 sub-dimensions: `[data — star_ratings_by_facility.csv, mean across all snapshots]`

| Dimension | Government | Not-for-Profit | For-Profit | Gap (Gov − FP) |
|-----------|-----------|----------------|------------|----------------|
| **Staffing** | **4.39** | 3.26 | **2.61** | **−1.78 pts** |
| Residents' Experience | 3.67 | 3.45 | 3.34 | −0.34 pts |
| Compliance | 4.69 | 4.60 | 4.54 | −0.15 pts |
| Quality Measures | 3.52 | 3.19 | 3.51 | ≈ 0 |

Staffing drives almost the entire 0.57-point gap. Health outcome measures (Quality Measures) are virtually identical across ownership types: 3.52 vs 3.51. For-profit facilities are not producing worse clinical results — they are deploying fewer staff hours to achieve them.

> **Dashboard callout (info):** The ownership gap is a staffing gap, not a clinical outcomes gap. Quality Measures scores are 3.52 (government) vs 3.51 (for-profit) — virtually identical.

---

### Insight 3 — The gap is not a geography artefact
A common counter-argument: government facilities score higher because they concentrate in rural areas with different resident mixes. The data rejects this.

Within each MMM band, government outperforms for-profit: `[data — star_ratings_by_facility.csv grouped by mmm_code × purpose_clean]`
- **MM1 (major city):** Government 4.03 vs For-Profit 3.50 — gap of **0.53 pts** in the most privatised, most competitive market
- **MM5 (small rural town):** Government 4.19 vs For-Profit 3.63 — gap **widens** to 0.56 pts in rural areas
- **MM6 & MM7 (remote/very remote):** No for-profit facilities operate here at all

Ownership type predicts quality inside every remoteness band, not because of where facilities are located.

> **Dashboard callout (warning):** The for-profit quality gap is not a geography artefact. Government outperforms for-profit inside every remoteness band from MM1 cities to MM5 rural towns. In rural areas, the gap widens.

---

### Insight 4 — Metro areas are the most privatised and the lowest quality
For-profit market share by remoteness band: `[data — star_ratings_by_facility.csv, facility count by mmm_code × purpose_clean]`

| Band | For-Profit facilities | Total | For-Profit share |
|------|-----------------------|-------|-----------------|
| MM1 Major city | 865 | 1,985 | **43.6%** |
| MM2 Inner regional | 69 | 240 | 28.7% |
| MM3 Outer regional | 56 | 258 | 21.7% |
| MM4 Remote | 40 | 222 | 18.0% |
| MM5 Small rural town | 32 | 359 | 8.9% |
| MM6 Remote community | 0 | 30 | **0%** |
| MM7 Very remote | 0 | 12 | **0%** |

This is why Chapter 1 shows patches of low quality in major cities — it's a concentration-of-for-profit problem, not a city infrastructure problem. Remote areas score higher on quality partly because they have zero for-profit presence.

> **Dashboard callout (info):** 43.6% of major city facilities are for-profit — the highest concentration of any remoteness band. In remote and very remote areas: 0%.

---

### Insight 5 — For-profit receives the most public funding per facility, yet scores lowest
Average government funding per facility in 2024: `[data — service_funding_by_facility.csv grouped by org_type, 2024]`

| Ownership | Funding per facility | Avg quality score |
|-----------|---------------------|-------------------|
| **For-Profit** | **$7.46M** | 3.50 |
| Not-for-Profit | $5.54M | 3.61 |
| Government | $2.85M | 4.07 |

For-profit receives **2.6× more** public funding per site than government-run facilities, yet scores 0.57 points lower on quality. The efficiency argument for privatisation does not hold in this data.

> **NFP caveat:** Not-for-profit (3.61) sits far closer to for-profit (3.50) than to government (4.07), despite receiving $5.54M per facility — nearly double government funding. The NFP quality advantage over for-profit is real but narrow (+0.11 pts). Framing NFP as simply "better than for-profit" understates how far both fall short of government.

**External context:** KPMG 2025 — 21 providers exited FY24; top 25 providers now hold **44.7% of all residential places**. `[external — KPMG Aged Care Sector Analysis 2025]` Government investment reached **$39.2B in FY25**, up 9.6%. The sector is consolidating while quality stagnates.

> **Dashboard callout (warning):** For-profit homes receive $7.46M per facility in government funding — 2.6× the rate of government-run homes — and return the lowest quality score of any ownership type.

---

### Insight 6 — The gap is consistent across time, not closing
Quarterly trend May 2023 → February 2026 (12 snapshots): `[data — star_ratings_by_facility.csv, grouped by purpose_clean × snapshot_date]`
- Government improved post-mandate; for-profit improved by a similar amount
- The structural gap between ownership types has **not narrowed**
- NFP sits between government and for-profit at every snapshot

The mandate addressed the level of care; it did not address the structural ownership gap.

---

## Tension — what makes this story not simple

Two complications to name honestly in the dashboard:

1. **Staffing gap ≠ clinical outcomes gap.** Quality Measures are near-identical (3.52 vs 3.51). For-profit may be operating with fewer staff hours while maintaining acceptable clinical floors. Whether that is efficiency or accumulated risk is a question this data cannot answer. ACQSC data shows neglect notifications rose 26% in the year after the mandate while star ratings rose simultaneously — both signals are real and measure different things.

2. **Confounders exist.** For-profit facilities cluster in major cities, tend to be larger, and serve a different patient mix. The correct framing: *ownership type is associated with lower quality, and the association holds within every geography band tested.* Not the same as "for-profit causes worse care" — but enough to warrant the question.

---

## Visuals for dashboard

| Visual | Type | Key finding surfaced |
|--------|------|---------------------|
| **1** | Scatter (access rate vs quality, MMM colour, OLS trendline, 2024) | SA3-level pattern; remote areas score higher |
| **2** | Scatter with year slider (2023–2024) | Year-on-year shift in SA3 distribution |
| **3** | Dual bar (facility count + funding by org type) | Market structure by ownership |
| **4** | Grouped bar (quality by ownership, over time) | Ownership gap consistent year-on-year |
| **5** | Grouped bar (quality by MMM band, ownership colour) | Gap holds within every remoteness band |
| **5b** | Stacked bar (facility count by MMM band, ownership colour) | For-profit concentrates at MM1 (43.6%); absent at MM6–MM7 |
| **6** | Grouped bar (sub-rating breakdown by ownership) | Staffing drives the gap; Quality Measures near-identical |
| **7** | Line chart (quarterly quality trend by ownership, mandate marked) | Gap stable; mandate lifted all types equally |
| **8** | Box plot (quality distribution by ownership) | For-profit more variable — some good, many mediocre |
| **9** | Horizontal bar (funding per facility + quality annotation) | Efficiency paradox — most funded, least quality |
| **9b** | Treemap (funding by org type) | Visual scale of funding concentration |

---

## Data sources used

| File | Columns used |
|------|-------------|
| `star_ratings_by_facility.csv` | `sa3_code`, `sa3_name`, `state`, `mmm_code`, `snapshot_date`, `quality_score`, `residents_exp`, `staffing`, `compliance`, `quality_measures`, `Purpose` |
| `service_users_by_sa3.csv` | `sa3_code`, `year`, `total_residential`, `total_homecare` |
| `abs_population_by_sa3.csv` | `sa3_code`, `year`, `pop_65_plus` |
| `service_funding_by_facility.csv` | `sa3_code`, `year`, `org_type`, `funding`, `service_name` |

**Key derived metrics:** `access_rate` = total_residential / pop_65_plus × 100 | `avg_quality` = mean quality_score per SA3 × year | `purpose_clean` normalised to Government / Not-for-Profit / For-Profit from raw `Purpose` field.

---

## External research citations

| Source | Stat | Use for |
|--------|------|---------|
| Chu et al., JAMDA 2024 (peer-reviewed, n=2,476) | For-profit OR 0.12 vs government for 4–5 stars — 8× less likely | Validates Insight 1 ownership gap |
| KPMG Aged Care Sector Analysis 2025 | 21 providers exited FY24; top 25 hold 44.7% of places; $39.2B govt investment FY25 | Validates Insight 5 consolidation |
| ACQSC December 2023 quarter | ~15% of facilities failing all 8 Quality Standards; Standard 3 and 8 worst compliance | Context for quality floor across sector |

---

## Note on demographic overlay

NESB and Indigenous demographic data (from CURF) is only available at **ACPR level (73 regions)**, not SA3. Do not attempt to join it to SA3 — the correspondence does not exist in the pipeline. Any demographic angle must be scoped to ACPR-level analysis only.
