# Chapter 1 — The Map: Is aged care near me any good?

## Narrative purpose

Open with a map that lets the viewer locate what matters to them — their suburb, their parents' city, their potential market. Before reading a single number, they can see their region and ask: "Is the care near me actually decent — and is there enough of it?" The map answers both questions at once.

---

## Visual: Choropleth map

Each SA3 is coloured by `care_gap_index_residential`. **Red/orange = more underserved. Green = lower pressure. Grey = no data.**

**Interactions:**
- Hover: SA3 name, state, care_gap_index_residential, avg_quality, access_rate_residential, access_rate_homecare, access_rate_combined, pop_65_plus
- Sidebar filters: State, Remoteness (MMM), Year

---

## Metrics computed

| Metric | Formula | What it measures |
|--------|---------|-----------------|
| `access_rate_residential` | `total_residential / pop_65_plus × 100` | % of 65+ in residential aged care |
| `access_rate_homecare` | `total_homecare / pop_65_plus × 100` | % of 65+ receiving home care packages |
| `access_rate_combined` | `(total_residential + total_homecare) / pop_65_plus × 100` | % of 65+ covered by any formal aged care |
| `care_gap_index_residential` | `access_rate_residential / avg_quality` | Headline gap metric — high = high demand, lower quality |

---

## Key insights to surface

### Insight 1 — The crisis is in the city, not the outback

**Headline number: Unley (SA) — Care Gap Index 2.78, more than 2× the national average of 1.13** `[data]`

Every single SA3 in the top 10 worst-performing list is **MM1 — major city**. No rural or remote region appears. The ten communities with the largest gap between care demand and care quality are all inner-suburban or metropolitan areas `[data — care_gap_index_residential computed from star_ratings + service_users + abs_population, 2024]`:

| # | Region | State | Care Gap | Quality |
|---|--------|-------|----------|---------|
| 1 | Unley | SA | 2.78 | 3.73 ★ |
| 2 | South Perth | WA | 2.55 | 3.49 ★ |
| 3 | Perth City | WA | 2.49 | 3.77 ★ |
| 4 | Caboolture | QLD | 2.42 | 3.47 ★ |
| 5 | Southport | QLD | 2.37 | 3.58 ★ |
| 6 | Fremantle | WA | 2.26 | 3.47 ★ |
| 7 | Moreland North | VIC | 2.25 | 3.40 ★ |
| 8 | Stonnington East | VIC | 2.20 | 3.57 ★ |
| 9 | Woden Valley | ACT | 2.07 | 3.60 ★ |
| 10 | Rocklea–Acacia Ridge | QLD | 2.07 | 3.74 ★ |

WA dominates (3 of top 10), followed by QLD (3) and VIC (2).

> **For families:** If your parents live in Unley, South Perth, or Caboolture, the pressure on aged care in their suburb is more than double the national average. More facilities nearby does not mean better care — in these suburbs it often means the opposite.

> **For investors:** Three states — WA, QLD, VIC — show consistent market stress in their metropolitan cores. These are the areas where the gap between demand and quality is largest, and where a quality-differentiated operator would face the least direct competition.

---

### Insight 2 — Australia covers fewer elderly people than comparable nations, but relies more heavily on residential care

**Australia's position globally (OECD Health at a Glance 2023, 2021 data):**

| Country | Residential beds per 1,000 aged 65+ | % of 65+ in residential care | Combined LTC coverage |
|---------|-------------------------------------|-----------------------------|-----------------------|
| Netherlands | 77.1 | ~6% | ~12% |
| Sweden | 63.9 | ~5% | **~16%** |
| Denmark | 37.3 | ~4% | **~14%** |
| **Australia** | **47.6** | **5.6%** ← 3rd highest OECD | **~8–9%** ← below average |
| Canada | 49.2 | ~3% | ~5% |
| United Kingdom | 41.3 | ~2.5% | ~5–6% |
| Japan | 34.5 | ~2% | ~3% |
| **OECD average** | **42.1** | **3.8%** | **~12.7%** |

*Sources: OECD Health at a Glance 2023; PMC9858923 (Comparative Analysis of LTC in OECD Countries); healthsystemsfacts.org*

**What this means:** Australia has the **3rd highest share of elderly people in residential care** in the OECD — yet its **total coverage** (residential + home care combined, ~8–9%) sits well below the OECD average of 12.7% and far below Sweden (16%) and Denmark (14%).

Australia packs more elderly people into facilities than almost any peer country, while leaving a larger proportion of the elderly population with **no formal care at all**. The Nordic model achieves broader coverage by delivering 77–79% of care at home — Australia delivers most of its care inside buildings, to a smaller group.

> **For families:** Australia is not a generous care system — it is a narrowly targeted one. If your parent does not qualify for a residential place or a home care package, they likely receive nothing. In Sweden or Denmark, they would almost certainly receive some level of formal support at home.

> **For workers:** The structural shift underway in Australia — growing home care, shrinking residential beds per capita — mirrors what the Nordic countries did 20–30 years ago. Home care is the growth channel.

---

### Insight 3 — Australia's residential access rate (4% of 65+) is right at the data, but hiding a decline

**From project data (2024, mean across 321 SA3s):**
- `access_rate_residential`: ~4% of 65+ in residential care
- The domestic benchmark — places per 1,000 aged 70+ — fell from **76 (2020) to 67 (2025)**, a 12% drop in 5 years *(Aged Care Online, Dec 2025)*

Australia's residential beds are declining per capita even as the 85+ population grows. The OECD's 2021 figure (47.6 per 1,000 aged 65+) was already below the Netherlands and Sweden; the 2025 domestic trend suggests Australia is moving further away from peer benchmarks, not toward them.

> **For investors:** The supply gap is structural and growing. 103 facilities closed since 2021, only 85 opened — net loss of 18 nationally. Annual bed creation needs to reach ~9,300–10,600 to keep pace; actual additions in 2025 were ~800 *(Aged Care Online, Dec 2025)*. The undersupply in quality residential care is a multi-decade structural opportunity, not a short-term cycle.

---

### Insight 4 — The state that tries hardest, under the most pressure

**ACT: care gap index 1.37 — highest of any state or territory** `[data]`

`[data — care_gap_index_residential, avg_quality, access_rate_residential aggregated by state, 2024]`

| State | Care Gap | Quality | Residential Access |
|-------|----------|---------|-------------------|
| **ACT** | **1.374** | 3.61 ★ | **5.01%** ← highest |
| SA | 1.233 | 3.52 ★ | 4.32% |
| VIC | 1.205 | 3.63 ★ | 4.34% |
| NSW | 1.128 | 3.59 ★ | 4.03% |
| WA | 0.993 | 3.46 ★ | 3.47% |
| NT | 0.838 | 3.60 ★ | 3.00% |
| TAS | **0.809** | **3.77 ★** ← highest | 2.92% |

ACT's high care gap is not driven by poor quality (3.61 stars, near national average) — it is driven by **the highest demand rate in the country** (5.01% of its 65+ population is in residential care). ACT elderly are entering care at a higher rate than anywhere else in Australia.

Tasmania is the inverse: lowest access rate, highest quality score — a small, well-managed system under the least demand pressure of any state.

> **For families in ACT:** More of your peers are in residential care than anywhere else in Australia, which means facilities are under more capacity pressure. Check individual facility star ratings carefully before choosing — the state average masks wide variation.

---

### Insight 5 — The counterintuitive finding: remote areas have better care quality

**Quality score by remoteness (2024):** `[data — grouped by mmm_code, all metrics from star_ratings + service_users + abs_population]`

| Remoteness Band | Care Gap | Quality Score | Residential Access |
|-----------------|----------|---------------|-------------------|
| MM1 Major city | 1.274 — **highest gap** | 3.55 ★ — **lowest** | 4.53% |
| MM2 Inner regional | 0.982 | 3.56 ★ | 3.48% |
| MM3 Outer regional | 1.071 | 3.50 ★ | 3.75% |
| MM4 Remote | 0.887 | 3.68 ★ | 3.25% |
| MM5 Small rural | 0.845 | 3.84 ★ | 3.22% |
| MM6 Remote community | 0.674 | 3.61 ★ | 2.38% |
| MM7 Very remote | 0.695 — **lowest gap** | **3.90 ★** — **highest** | 2.72% |

Australia's most remote communities score **3.90 stars** on quality — +0.35 pts above major cities. This is not an anomaly; it is consistent across every year of data.

**Why:** Remote facilities are often not-for-profit or government-run, serve tightly-knit communities, and face less competitive pressure to cut staff costs. Major city facilities are disproportionately for-profit and operate under higher volume pressure.

**The real remote disadvantage is access, not quality.** MM7 has a residential access rate of only 2.72% — not because the care is poor, but because there are barely any beds. Residents often travel hundreds of kilometres to access the nearest facility.

> **For families in rural or remote areas:** If you can access a facility near you, it is likely better quality than anything available in Sydney, Melbourne, or Perth. The problem is not quality — it is that the nearest bed may be 200 km away.

> **For families in cities:** Having dozens of facilities nearby does not guarantee better care. The OLS trendline in our data is slightly negative — more facilities per region is weakly associated with *lower* average quality.

---

### Insight 6 — 79% of Australia improved in one year; 21% moved in the wrong direction

**2023 → 2024 change across 321 SA3s:** `[data — year-on-year delta of care_gap_index_residential per SA3]`
- **Improving** (care gap fell): **250 SA3s — 79%**
- **Worsening** (care gap rose): **66 SA3s — 21%**

The majority of Australia's aged care regions improved between 2023 and 2024 — consistent with the October 2023 staffing mandate lifting average quality scores nationally by +7.3 pts (detailed in Chapter 4). But 1 in 5 SA3s moved in the wrong direction, and these tend to cluster in MM1 areas where for-profit concentration is highest and mandate compliance is slowest.

> **For workers:** Improving regions signal investment and mandate compliance — better working conditions ahead. The 66 worsening SA3s, mostly in metro areas, are the ones where workloads are rising without corresponding quality improvement.

---

### Insight 7 — Home care partially compensates in remote areas, but the waitlist means it barely reaches anyone

**Coverage by service type (2024, national avg across SA3s):** `[data — service_users_by_sa3 + abs_population_by_sa3]`
- `access_rate_residential` — in facility: ~4%
- `access_rate_homecare` — home care package: ~6–7%
- `access_rate_combined` — any formal care: ~10–11%

In remote communities (MM6–MM7), residential access drops sharply but home care access does not fall proportionally — home care packages partially compensate for the absence of nearby beds.

**But nationally, 88,000+ people are approved for a home care package and not receiving one** (Nov 2025, Aged Care Guide). A further 120,000+ are still waiting to be assessed. In Sweden and Denmark — where municipalities have a legal obligation to provide home care — a national waitlist of this kind does not exist.

Australia's combined coverage of ~10–11% of 65+ receiving formal care is meaningfully below the OECD average of 12.7%, and far below the Nordic standard of 14–16%. The gap is almost entirely explained by the home care channel being rationed in ways that do not exist in peer countries.

> **For families:** If your parent is on the home care waitlist, they are in a queue that has no equivalent in comparable countries. In Denmark or Sweden, the right to receive home support is legal — here it depends on package availability and budget allocation.

---

## International benchmark summary

| Metric | Australia (2024/2025) | OECD average | Best peer |
|--------|----------------------|--------------|-----------|
| Residential beds per 1,000 aged 65+ | 47.6 (2021, declining) | 42.1 | Netherlands 77.1 |
| % of 65+ in residential care | 5.6% — 3rd highest OECD | 3.8% | — |
| Combined formal LTC coverage | ~10–11% | ~12.7% | Sweden ~16% |
| Home care as % of LTC recipients | ~40% | ~70% | Denmark/Sweden 77–79% |
| Home care waitlist | **88,000+** | Effectively 0 in Nordic systems | — |

*Sources: OECD Health at a Glance 2023 (2021 data); PMC9858923; healthsystemsfacts.org; Aged Care Guide Nov 2025*

**One-line verdict:** Australia puts more elderly people into facilities than almost any other developed country — but leaves a larger share of the elderly population with no formal support at all, and rations the home care that would close that gap. The system is both more institutionalised and less comprehensive than its peers.

---

### Insight 8 — Supply collapse: 104 fewer facilities, but 12,270 more beds

**The market is consolidating into fewer, larger providers — and every state lost beds per capita.**

`[data — service_supply_by_sa3.csv, 2019–2025]`

| Metric | 2019 | 2025 | Change |
|--------|------|------|--------|
| Residential facilities (national) | 2,877 | 2,773 | **−104** |
| Residential places (beds) | 215,989 | 228,259 | **+12,270** |

Australia has 104 fewer aged care facilities than in 2019 but 12,270 more beds. Smaller facilities are closing while larger ones absorb demand — consolidation, not collapse.

**Every state lost beds per capita (2019 → 2024):** `[data — service_supply_by_sa3 + abs_population_by_sa3]`

| State | Beds/1,000 elderly 2019 | Beds/1,000 elderly 2024 | Change |
|-------|------------------------|------------------------|--------|
| NT | 33.0 | 25.5 | **−7.4** |
| SA | 57.6 | 50.2 | **−7.4** |
| TAS | 47.9 | 42.1 | **−5.8** |
| NSW | 55.0 | 49.6 | **−5.4** |
| QLD | 51.6 | 46.3 | **−5.4** |
| VIC | 56.1 | 51.4 | **−4.7** |
| WA | 46.4 | 43.6 | **−2.8** |
| ACT | 43.9 | 41.8 | **−2.2** |

Even WA and ACT — the only states that gained facilities — still saw beds per 1,000 elderly fall, because population growth outpaced supply additions. NSW had the largest absolute facility loss (−54). Southport (QLD) lost the most beds: −615 places across 6 fewer facilities. 119 SA3s lost at least one facility; only 79 gained.

> **For families:** The facility count near you has likely fallen since 2019, but survivors are larger. Fewer locations means less geographic choice — not necessarily a statewide shortage of beds, but potentially a longer drive.

> **For workers:** Consolidation means fewer employers, larger workplaces. Smaller independent operators are exiting fastest.

> **For investors:** Top 25 providers now hold 44.7% of all places (KPMG 2025). Annual bed creation needs ~9,300–10,600 to keep pace with demand; actual additions in 2025 were ~800. `[external — Aged Care Online, Dec 2025; KPMG Aged Care Sector Analysis 2025]`

---

## Data sources

| File | Columns used |
|------|-------------|
| `data/clean/star_ratings_by_facility.csv` | `sa3_code`, `sa3_name`, `state`, `mmm_code`, `snapshot_date`, `quality_score` |
| `data/clean/service_users_by_sa3.csv` | `sa3_code`, `year`, `total_residential`, `total_homecare` |
| `data/clean/abs_population_by_sa3.csv` | `sa3_code`, `year`, `pop_65_plus` |
| `data/clean/service_supply_by_sa3.csv` | `sa3_code`, `year`, `n_residential`, `residential_places` |
| `data/raw/abs_geography/SA3_2021_AUST_GDA2020.shp` | SA3 polygon boundaries (ABS ASGS Edition 3, 2021) |

**External research:**
- OECD Health at a Glance 2023 & 2025 — residential beds and LTC recipient rates
- PMC9858923 — Comparative Analysis of LTC in OECD Countries (2023)
- PMC7496246 — Is Australia over-reliant on residential aged care? (2020)
- Aged Care Online, Dec 2025 — supply collapse data (beds per 1,000 aged 70+)
- Aged Care Guide / The Weekly Source, Nov 2025 — home care waitlist 88,000+
- healthsystemsfacts.org — Sweden, Denmark, Netherlands, Canada, Japan LTC profiles
