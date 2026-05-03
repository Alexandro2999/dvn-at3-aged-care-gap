# Chapter 4 — The Mandate Effect

**Question:** Is the system improving?  
**Answer:** Yes — on inputs. Not yet — on outcomes for residents.

---

## Background: Why was a mandate needed?

- In 2021, the Royal Commission into Aged Care found **57.6% of residents** were living in facilities with unacceptable staffing levels
- Before the mandate, providers set their own staffing levels — no mandatory minimum floor existed
- Commission finding: *"Providers are free to judge for themselves what staffing numbers are 'adequate'. The status quo is unacceptable."*
- Deloitte projected a **70% workforce increase** (186k → 316k FTE) needed from 2020–2050 just to maintain the current staffing ratio

---

## What the mandate requires

| Date | Requirement |
|------|-------------|
| 1 Jul 2023 | Registered nurse on-site **24/7** at every residential facility |
| **1 Oct 2023** | Minimum **200 minutes** direct care per resident per day, of which at least **40 minutes** must be a registered nurse |
| 1 Oct 2024 | Raised to **215 minutes** total / **44 minutes** RN |

---

## Insight 1 — The mandate worked: national quality rose +7.4%

- National average quality score: **3.40 → 3.65** (+0.25 pts) after Oct 2023
- The increase is a clear step-change — not a slow trend; visible across every state within two quarters
- All 8 states and territories improved in absolute terms
- **Source:** star_ratings_by_facility.csv — before/after Oct 2023

---

## Insight 2 — Staffing was the only dimension that truly moved

| Sub-rating | Before | After | Change |
|-----------|--------|-------|--------|
| Staffing | 2.49 | 3.00 | **+0.51 pts** |
| Compliance | 4.28 | 4.57 | +0.29 pts |
| Residents experience | 3.28 | 3.50 | +0.22 pts |
| **Quality measures** | 3.55 | 3.54 | **−0.015 pts** |

- Staffing recorded the largest gain — consistent with the mandate's design
- Quality measures (resident health outcomes) were essentially flat
- Independent research by **SAHMRI / Flinders University (2025)** across 2,000+ facilities confirms: *"Despite rising staffing levels, no meaningful association emerged between increased care minutes and improved resident quality measures."* — A/Prof Stephanie Harrison
- The mandate improved inputs. Outcomes have not yet followed.

---

## Insight 3 — Real-world compliance is far lower than expected

- Before the mandate, only an estimated **3.8%** of facilities were positioned to meet the new standards *(The Conversation)*
- 2023–24: only **34%** of facilities met both targets simultaneously (total + RN minutes) — *Productivity Commission 2025*
- 24/7 RN requirement reached **93.5%** compliance — easier to measure and enforce than care minutes
- January 2025: ACQSC enforced against **11 providers / 27 facilities** — capped at 1 star, banned from reaching 5 stars for 3 years
- Star ratings reward improvement effort, not only full compliance — which explains why the staffing sub-rating rose +0.51 pts despite only 1 in 3 facilities being fully compliant

---

## Insight 4 — States: NT surges, VIC falls behind

| State | Change | Rank: first → latest |
|-------|--------|----------------------|
| NT | **+0.748 pts** | 7 → **1** |
| VIC | +0.312 pts | **1 → 5** |
| ACT | +0.306 pts | smallest gain |

- NT started from the lowest base and improved the most — the mandate had the greatest impact where the gap was largest
- VIC did not worsen in absolute terms — other states simply caught up faster
- No state declined in absolute terms
- **Source:** star_ratings_by_facility.csv — first snapshot (May 2023) vs latest (Feb 2026)

---

## Insight 5 — 17 SA3 regions are still declining

- **302 / 323 SA3 regions** show an improving quality trend
- **17 / 323 SA3 regions** are still declining — the mandate has not reached them
- Worst: **Esperance (WA)** — −0.07 pts/quarter
- Gold Coast Hinterland and Port Douglas–Daintree (QLD) are also in the declining group
- **Source:** linear regression slope on quality_score over quarters, minimum 4 snapshots

---

## Insight 6 — Workforce gap by geography (context for at-risk SA3s)

- Metro: **317 aged care workers** per 1,000 people aged 65+
- Rural: **256** per 1,000
- Remote: **245** per 1,000
- To reach metro parity: rural areas need ~**95,342 additional FTE**; remote areas need ~**12,958 additional FTE**
- **Source:** Morris et al., IJERPH April 2025 (peer-reviewed)

---

## Framing

| Level | Message |
|-------|---------|
| National | The mandate worked — +7.4% is a measurable step-change |
| Sub-rating | But it only fixed staffing inputs, not resident outcomes |
| SA3 | In 17 communities, the mandate has not yet landed |
| Tone | Cautious optimism — improving, but not enough and not evenly |
