# Chapter 3 — The Reveal: The waitlist is real — and it's getting longer

## Narrative purpose

Numbers become people. After Chapter 1 mapped the gap and Chapter 2 named the culprit (ownership type), Chapter 3 names the 20 communities where elderly Australians with high care needs are stuck waiting — often over a year — because there simply are not enough beds. The data reveals a system using home care as a holding pen for people who clinically belong in residential care.

**Narrative arc:** The Detective — resolution. This is where the national pattern becomes specific: named places, named numbers, named people.

---

## Opening question by audience

| Audience | Their question |
|----------|---------------|
| **Families** | Is my region on the list? How long would my parent actually wait for a bed? |
| **Workers entering the sector** | Where is demand so high that job security is guaranteed? |
| **Businesses / investors** | Which regions have documented, growing, unmet demand — and are underserved by current operators? |

---

## Key insights

### Insight 1 — Home care is doing residential's job

Australia's home care system was built to support light daily needs at home. It has become something else entirely.

**59.1% of all home care approvals in 2025 are Level 3 or Level 4** — the two highest care tiers, representing people who require significant daily assistance or near-constant clinical support. `[data — service_users_by_sa3.csv, 2025]`

The L3+L4 population grew from **140,968 (2023) to 172,285 (2025) — a +22% rise in two years.** `[data — service_users_by_sa3.csv, 2023–2025]` These are not people choosing to age at home with light support. They are people whose assessments say they belong in residential care, but who are sitting in the home care system because there are no beds to move them into.

**External context:** As of November 2025, **88,000+ people** had been approved for home care packages but were not yet receiving them — with a further **120,000+ waiting to be assessed**. `[external — Aged Care Guide / The Weekly Source, Nov 2025]` National peak bodies including National Seniors, OPAN, and ACCPA report **12–15 month waits** after approval as becoming standard. `[external — National Seniors Australia / Senate Committee submissions, 2025]`

> **Dashboard callout (warning):** 59.1% of all home care approvals are now Level 3 or Level 4. These 172,285 people need residential care — but the beds are not there.

---

### Insight 2 — 58 communities in structural deficit

`waitlist_pressure` = hcp_high_needs ÷ residential_places. When pressure exceeds 1.0, demand structurally exceeds supply.

In 2024: `[data — service_users_by_sa3.csv + service_supply_by_sa3.csv, 2024]`
- **58 SA3 regions** have more high-needs home care users than available residential beds (pressure > 1.0) — nearly 1 in 6 of all analysed regions
- **8 regions** have demand more than double the supply (pressure > 2.0)
- **National median pressure: 0.636** — even in a typical region, 6 people with high-level needs are waiting for every 10 beds

The worst case nationally: **Central Highlands (Tas.) at 3.111** — 56 people competing for 18 beds. For a family in this region, finding a residential bed is not difficult. It is effectively impossible.

> **Dashboard callout (warning):** 58 SA3 regions — nearly 1 in 6 nationally — have more high-needs people than available residential beds. Central Highlands (Tas.) has 3.1 people for every 1 bed.

---

### Insight 3 — This is not a remote problem

The assumption that aged care crisis is concentrated in rural or remote areas does not hold.

**12 of the 20 worst-pressure regions are MM1 major cities.** `[data — service_users_by_sa3.csv + service_supply_by_sa3.csv + star_ratings_by_facility.csv, 2024]` The crisis is geographic — about where beds are — not demographic.

Top 5 worst regions by waitlist pressure:

| SA3 | State | MMM | Pressure | Beds | HCP L3+L4 |
|-----|-------|-----|----------|------|-----------|
| Central Highlands (Tas.) | TAS | MM5 | 3.111 | 18 | 56 |
| Noosa Hinterland | QLD | MM2 | 2.833 | 90 | 255 |
| Sunshine Coast Hinterland | QLD | MM1 | 2.615 | 252 | 659 |
| Wheat Belt - North | WA | MM4 | 2.612 | 369 | 964 |
| Gympie - Cooloola | QLD | MM3 | 2.324 | 445 | 1,034 |

`[data — service_users_by_sa3.csv + service_supply_by_sa3.csv, 2024]`

> **Dashboard callout (info):** 12 of the 20 worst waitlist-pressure regions are MM1 major cities. This is not a remote problem — it is a supply problem in the places where most Australians live.

---

### Insight 4 — The problem is supply, not demand

The three-tier access rate analysis reveals why high-pressure regions are in crisis — and it is not because elderly people there are avoiding the system.

Average access rates by pressure group, 2024: `[data — service_users_by_sa3.csv + service_supply_by_sa3.csv + abs_population_by_sa3.csv, 2024]`

| Group | Residential % | HCP High % | Combined % |
|-------|--------------|------------|------------|
| Low pressure (≤1.0) | 4.36% | 2.79% | 9.66% |
| High pressure (>1.0) | 2.68% | 4.15% | 9.19% |

**Combined access is nearly identical** — ~9.2% vs 9.7% of the elderly population. People in crisis regions are using the aged care system at the same rate as elsewhere. The difference is which tier they are stuck in.

In high-pressure regions, the ratio has flipped: more elderly people are receiving high-needs home care than are in residential care. **19 of the 20 worst-pressure regions** have higher HCP L3+L4 access than residential access per capita. `[data — join, 2024]` The top 20 worst regions average a residential access rate of **1.84%** — less than half the national median of **4.02%**. `[data — join, 2024]`

> **Dashboard callout (warning):** In crisis regions, high-needs home care users outnumber residential users per capita — 19 of the 20 worst regions. The system is reaching people. It is just not reaching them with the right type of care.

---

### Insight 5 — Getting worse: +10 crisis zones in 12 months

The list of crisis communities is not static. Between 2023 and 2024: `[data — service_users_by_sa3.csv + service_supply_by_sa3.csv, 2023–2024]`

- **14 new SA3 regions crossed the pressure = 1.0 threshold** for the first time
- Only **4 communities** resolved their deficit
- Net change: **+10 crisis zones in 12 months**

The new entrants span every geography — NT, WA, SA, VIC, TAS, QLD — and all remoteness bands from MM1 cities (Sunbury VIC, Campbelltown SA, Dandenong VIC) to MM4–5 rural areas. This is a national pattern expanding, not a regional problem migrating.

The underlying driver is demographics. Australia's 65+ population grew from **4.03 million (2019) to 4.70 million (2024)** — an increase of 670,000 people in five years. `[data — abs_population_by_sa3.csv, 2019–2024]` GEN quarterly data records **87,597 people on the National Priority List** as at March 2025. `[external — GEN quarterly data / National Seniors Australia, 2025]`

> **Dashboard callout (warning):** 14 new communities became crisis zones in a single year. Only 4 resolved their deficit. Net: +10 in 12 months.

---

### Insight 6 — Double crisis: low supply and low quality

Some communities face both problems simultaneously. `[data — join, 2024]`

| SA3 | State | Pressure | Quality score |
|-----|-------|----------|---------------|
| The Hills District | QLD | 2.029 | **2.969** |
| Kwinana | WA | 2.024 | **3.188** |
| Mundaring | WA | 1.677 | **2.857** |

For families in these communities, the crisis is not just about how long the wait is. It is about whether the care available at the end of the wait is safe.

**The system-wide cost extends beyond families.** In 2022–23, **438,779 hospital bed-days** were consumed by patients waiting for aged care placement. `[external — Aged Care Online, Dec 2025]` A further **2,500 elderly patients** are currently medically cleared but stuck in hospital waiting for aged care. `[external — Aged Care Online, Dec 2025]` **10% of hospital beds** nationally are occupied by patients who cannot be discharged because aged care is unavailable. `[external — Aged Care Guide, Nov 2025]`

> **Dashboard callout (error):** Some communities face both a waitlist and a quality crisis simultaneously. The Hills District (QLD): pressure 2.03 and quality score 2.97 — below the national floor.

---

### Insight 7 — Supply divergence: beds being built in the wrong places

`[data — service_supply_by_sa3.csv + service_users_by_sa3.csv, 2019–2024]`

| Group | Places 2019 | Places 2024 | Change |
|-------|-------------|-------------|--------|
| 58 crisis SA3s (pressure > 1.0) | 26,587 | 26,036 | **−551** |
| Rest of Australia | 189,402 | 201,429 | **+12,027** |

The 58 communities in structural deficit collectively lost 551 residential places between 2019 and 2024. Over the same period, the rest of Australia added 12,027 — a 6% increase. Supply is growing nationally, but systematically missing the communities where demand is highest.

Combined with the demand surge — L3+L4 home care users grew +22% in two years — the result is a double squeeze in crisis zones: demand surged while supply contracted.

> **For investors:** The 58 crisis zones have documented demand, contracting supply, and no new entrants — the clearest market signal in the dataset.

> **Dashboard callout (error):** Crisis zones lost 551 residential places between 2019 and 2024 while the rest of Australia added 12,027. New supply is going to regions that already have enough — not to the 58 communities where demand has outrun capacity.

---

## Tension — what makes this story not simple

**1. `waitlist_pressure` is a structural signal, not a perfect count.** It measures L3+L4 home care users against residential places — a reasonable proxy for unmet residential demand. But some people at L3+L4 genuinely prefer home care. The metric captures system-level mismatch, not individual preference. The 59.1% L3+L4 share and the +22% growth in two years suggest the accumulation is structural, not a matter of individual choice.

**2. The 88,000+ national waitlist figure and the project's 172,285 L3+L4 figure measure different things.** The 88,000+ (external — Aged Care Guide) counts people approved for home care packages but not yet receiving any support. The 172,285 counts people already receiving home care at the highest two need levels. These populations overlap but are not the same — both signals point to the same crisis, measured from different angles.

---

## Visuals for dashboard

| Visual | Type | Key finding surfaced |
|--------|------|---------------------|
| **A** | Stacked area (HCP levels by year, 2023–2025) | L3+L4 growing as share of all home care — structural shift, not noise |
| **B** | Horizontal bar (top 20 SA3 by pressure, MMM colour) | 58 regions in crisis; 12/20 are MM1 cities |
| **C** | Grouped horizontal bar (residential % vs HCP high % per capita, top 20) | Supply is the constraint — combined access nearly identical across pressure groups |
| **D** | Stacked bar (HCP levels 1–4 for top 20 regions) | 65.8% of home care users in worst regions are L3+L4 |
| **E** | Detail table (top 20 with pressure, beds, quality, access rates) | Double crisis — pressure + quality risk in same communities |
| **F** | Bar chart (communities crossing 1.0 threshold 2023→2024) | +14 new, −4 resolved, net +10 in 12 months |
| **G** | Dual line chart (residential places indexed to 2019, crisis vs non-crisis) | Crisis zones lost 551 beds; rest of Australia gained 12,027 — supply going to wrong places |

---

## Data sources used

| File | Columns used |
|------|-------------|
| `service_users_by_sa3.csv` | `sa3_code`, `sa3_name`, `year`, `hcp_level1`–`hcp_level4`, `hcp_high_needs`, `total_homecare`, `total_residential` |
| `service_supply_by_sa3.csv` | `sa3_code`, `year`, `residential_places`, `n_residential` |
| `abs_population_by_sa3.csv` | `sa3_code`, `state`, `year`, `pop_65_plus` |
| `star_ratings_by_facility.csv` | `sa3_code`, `mmm_code`, `quality_score` (aggregated per SA3) |

**Key derived metrics:**
- `waitlist_pressure` = hcp_high_needs / residential_places
- `access_rate_residential` = total_residential / pop_65_plus × 100
- `access_rate_homecare` = total_homecare / pop_65_plus × 100
- `access_rate_combined` = (total_residential + total_homecare) / pop_65_plus × 100
- `access_rate_hcp_high` = hcp_high_needs / pop_65_plus × 100

**Exclusions:** SA3 10702 (Illawarra Catchment Reserve, pop_65_plus = 0); SA3s with residential_places = 0 (no beds to compute pressure).

---

## External research citations

| Source | Stat | Used in |
|--------|------|---------|
| Aged Care Guide / The Weekly Source, Nov 2025 | 88,000+ approved, not receiving; 120,000+ waiting assessment; 10% hospital beds blocked | Insight 1, Insight 6 |
| National Seniors Australia / Senate submissions, 2025 | 12–15 month waits standard; 87,597 on National Priority List (Mar 2025) | Insight 1, Insight 5 |
| Aged Care Online, Dec 2025 | 438,779 hospital bed-days (2022–23); 2,500 patients stuck in hospital | Insight 6 |

---

## Note on demographic data limitation

NESB and Indigenous demographic breakdown is only available at **ACPR level (73 regions)** — it cannot be joined to SA3. This chapter does not include demographic equity analysis at the SA3 level. Any demographic angle must be scoped as a separate ACPR-level chart, clearly labelled as a different geographic unit.
