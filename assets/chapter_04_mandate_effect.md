# Chapter 4 — The Mandate Effect

**Question:** Has the government's staffing mandate actually improved care?  
**Answer:** Facilities are hiring more staff. But residents aren't living better for it yet.

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

## Insight 1 — Your facility is probably better than it was 2 years ago

- National average quality score: **3.40 → 3.65** (+0.25 pts) after Oct 2023
- The increase is a clear step-change — not a slow trend; visible across every state within two quarters
- All 8 states and territories improved in absolute terms
- **Source:** star_ratings_by_facility.csv — before/after Oct 2023

---

## Insight 2 — More staff, same health outcomes — the numbers tell an uncomfortable truth

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

## Insight 3 — Only 1 in 4 facilities actually met the new rules at launch

- Before the mandate, only an estimated **3.8%** of facilities were positioned to meet the new standards *(The Conversation)*
- From project data (facility-specific ACQSC targets): **26.1%** fully compliant at Dec 2023, consistent with Productivity Commission's 34% for full FY 2023–24
- 24/7 RN requirement reached **93.5%** compliance — easier to measure and enforce than care minutes
- January 2025: ACQSC enforced against **11 providers / 27 facilities** — capped at 1 star, banned from reaching 5 stars for 3 years
- Star ratings reward improvement effort, not only full compliance — which explains why the staffing sub-rating rose +0.51 pts despite only 1 in 3 facilities being fully compliant at mandate launch

---

## Insight 4 — NT went from last to first — VIC got left behind as other states caught up

| State | Change | Rank: first → latest |
|-------|--------|----------------------|
| NT | **+0.796 pts** | 8 → **1** |
| VIC | +0.311 pts | **1 → 5** |
| ACT | +0.289 pts | smallest gain |

- NT started from the lowest base and improved the most — the mandate had the greatest impact where the gap was largest
- VIC did not worsen in absolute terms — other states simply caught up faster
- No state declined in absolute terms
- **Source:** star_ratings_by_facility.csv — first snapshot (May 2023) vs latest (Feb 2026)

---

## Insight 5 — 16 regions are still going backwards — is yours one of them?

- **303 / 323 SA3 regions** show an improving quality trend
- **16 / 323 SA3 regions** are still declining — the mandate has not reached them
- Worst: **Esperance (WA)** — −0.07 pts/quarter
- Gold Coast Hinterland and Port Douglas–Daintree (QLD) are also in the declining group
- **Source:** linear regression slope on quality_score over quarters, minimum 4 snapshots

---

## Insight 6 — Rural areas need 95,000 more workers just to match city staffing levels

- Metro: **317 aged care workers** per 1,000 people aged 65+
- Rural: **256** per 1,000
- Remote: **245** per 1,000
- To reach metro parity: rural areas need ~**95,342 additional FTE**; remote areas need ~**12,958 additional FTE**
- **Source:** Morris et al., IJERPH April 2025 (peer-reviewed)

---

## Insight 7 — The mandate failed hardest in the places that needed it most

- **MM5 small rural towns are 2.38x overrepresented** among declining SA3s — 11.8% (4/34) of MM5 SA3s are declining vs only 3.8% of metro SA3s
- These regions operate with **256 aged care workers per 1,000 elderly** — 19% fewer than metro (317). The mandate cannot take hold where there are not enough workers to hire.
- **7 of 16 declining SA3s (44%)** are in rural/remote workforce tiers (MM3+), which represent only 34% of all SA3s
- **Queensland is a separate story:** 7 of 16 declining SA3s are in QLD (44%), 5 of them in metro areas — not a workforce gap problem, a state-specific concentration issue requiring its own investigation
- **Source:** quality_trend_slope from star_ratings_by_facility.csv × Morris et al. IJERPH 2025

---

## Insight 8 — Private facilities lag 54 percentage points behind government on compliance

- Fully compliant facilities: **26.1% (Dec 2023) → 65.2% (Feb 2026)** — improving steadily over 2 years
- When the target was raised in Oct 2024 (200→215 min / 40→44 RN), compliance dipped before recovering — providers are actively adapting, not stagnating
- **For-profit facilities are the least compliant** ownership type across all post-mandate snapshots: government 84.1% fully compliant vs for-profit 30.2% — a 54 percentage-point gap
- **Counter-intuitively, compliance is higher in remote areas** (MM7: 82.9%, MM6: 68.1%, MM5: 57.1%) than metro (MM1: 43.3%) — driven by the higher share of government-run facilities in remote regions, which outperform on compliance regardless of geography
- **Source:** facility-specific targets from ACQSC "Detailed data" sheet — `rn_minutes_actual >= rn_minutes_target` AND `total_minutes_actual >= total_minutes_target`

---

## Framing

| Audience | Message |
|----------|---------|
| For families | Average facility quality has genuinely risen since Oct 2023 — the system is better than it was |
| Watch out | The improvement is mostly on paper (staff headcount), not in resident health outcomes — quality measures flat at −0.015 pts |
| Your region | 16 communities are still declining — check if yours is one of them |
| For businesses entering the sector | Compliance pressure is real: only 26% fully compliant at mandate launch, rising to 65% by Feb 2026 — operators who can't meet standards are being squeezed out |
| Tone | Cautiously improving — but not fast enough, and not evenly |
