# Clean Data — File Dictionary

All files in this folder are outputs of the clean pipeline (`notebooks/clean_pipeline/`).
**Do not edit manually.** Re-run the corresponding notebook to regenerate.

Each entry below lists: **grain** (one row per …), **provenance** (raw source file + publisher),
**columns** with **name · type · description**, and any join keys.

---

## Raw data sources (provenance overview)

| Publisher | Source files (`data/raw/`) | Goes into |
|---|---|---|
| **ACQSC** — Aged Care Quality and Safety Commission, quarterly Star Ratings extract | `star_ratings/star-ratings-quarterly-data-extract-*.xlsx` × 12 (May 2023 → Feb 2026) | File 01 |
| **AIHW GEN** — Aged Care Service List, annual snapshot | `service_list/Australia*.xlsx` × 7 (2019 → 2025) | File 02 |
| **AIHW GEN** — People using aged care by region (SA3), annual snapshot | `service_users_snapshot_SA3/GEN-data-People-using-aged-care-by-region-30-June-*.xlsx` (2023, 2024, 2025) | File 03 |
| **AIHW GEN / CURF** — Admissions into aged care (home care branch). CURF for FY 2023–24, GEN aggregate for FY 2019–20 and 2020–21 | `admission/Admissionshomecare_*_GENdata.xlsx`, `admission/CURF_Admissions-into-aged-care_2023-24.xlsx` | File 04 |
| **AIHW GEN / CURF** — People using home care services (national) | `service_users_CURF/People-using-aged-care-services-30-June-*.xlsx`, `service_users_CURF/CURF_People-using_aged_care-2024.xlsx` | File 05 |
| **AIHW GEN / CURF** — Admissions into aged care (residential branch) | `admission/Admissionsresidential_*_GENdata.xlsx`, same CURF admission file as File 04 | File 06 |
| **AIHW GEN / CURF** — People using residential care services (national) | Same CURF service-user files as File 05 | File 07 |
| **AIHW GEN** — Service-level subsidy / funding extract | (sourced via GEN funding download, joined to service-list facility key) | File 08 |
| **ABS** — Estimated Resident Population by SA3, ABS catalogue 3235.0 Table 3 (Persons) | `abs_population/32350DS0005_2001-24.xlsx` | File 09 |

> **Provenance note:** ACQSC = Aged Care Quality and Safety Commission (regulator).
> AIHW GEN = the Australian Institute of Health and Welfare's **GEN Aged Care Data** portal (aggregated public release).
> CURF = AIHW's **Confidential Unit Record File** (individual-level deidentified data, accessed by approved users).
> ABS = Australian Bureau of Statistics.

---

## 00 — `master_sa3.csv` — **headline dataset for the dashboard**

**Source notebook:** `notebooks/architect/02_metrics.ipynb`
**Inputs joined:** files 01, 02, 03, 09 (and file 02 row from year=2019 for `supply_change` baseline)
**Grain:** one row per **SA3 × year** (years: 2023, 2024)
**Rows:** 660 · **Unique SA3s:** 330 (per year) · **Columns:** 28

This is the only file `dashboard/app.py` reads for SA3-level metrics — every chart in Ch 1–3
plots directly from it. Built by joining users + supply + population + (aggregated) quality,
then computing the six derived metrics in the **Derived metrics** section below.
SA3 `10702` (Illawarra Catchment Reserve — conservation land, `pop_65_plus = 0`) is excluded.

| Column | Type | Description |
|---|---|---|
| `sa3_code` | int | 5-digit SA3 code (ABS 2016 boundaries) — join key |
| `sa3_name` | str | SA3 name |
| `state` | str | State / territory (NSW, VIC, QLD, SA, WA, TAS, NT, ACT) |
| `year` | int | Reporting year (2023 or 2024) |
| `mmm_code` | str | Modified Monash Model band (MM1 = major city → MM7 = very remote). Mode of `mmm_code` across facilities in the SA3 |
| `pop_65_plus` | float | Estimated population aged 65+ (ABS, 30 June reference) |
| `total_pop` | float | Total estimated resident population |
| `n_facilities` | int | Total aged-care services in the SA3 (residential + home-care + multi-purpose) |
| `n_residential` | int | Residential-care services (incl. multi-purpose) |
| `residential_places` | float | Licensed residential beds in the SA3 |
| `n_nfp` | int | Facilities run by not-for-profit (Charitable / Religious / Community-Based) |
| `n_government` | int | Facilities run by government (State / Local / Territory) |
| `n_private` | int | Facilities run by for-profit (Private Incorporated Body / Publicly Listed) |
| `total_residential` | float | Permanent + respite residential care users (SA3 of residence) |
| `total_homecare` | int | Total home-care users (HCP packages active) |
| `total_users` | float | All aged-care users = `total_residential + total_homecare` |
| `hcp_level1` | int | Home Care Package Level 1 users (basic needs) |
| `hcp_level2` | int | HCP Level 2 users (moderate) |
| `hcp_level3` | int | HCP Level 3 users (high) |
| `hcp_level4` | int | HCP Level 4 users (very high) |
| `hcp_high_needs` | int | `hcp_level3 + hcp_level4` — proxy for clinical need that would normally warrant a residential bed |
| `quality_score` | float | Mean of the 4 ACQSC sub-ratings (`residents_exp + staffing + compliance + quality_measures`) / 4, averaged across all facilities in the SA3 for that year. Range 1–5. `NaN` when SA3 has no rated facility |
| `access_rate` | float | **Derived.** `total_residential / pop_65_plus × 100` — % of 65+ population in residential care |
| `care_gap_index` | float | **Derived. Headline metric.** `access_rate / quality_score` — high = high access but low quality (the metro for-profit pattern) |
| `waitlist_pressure` | float | **Derived.** `hcp_high_needs / residential_places` — > 1.0 means more L3/L4 home-care users than available beds (a "crisis zone") |
| `beds_per_1k` | float | **Derived.** `residential_places / pop_65_plus × 1000` — beds per 1,000 elderly |
| `private_share` | float | **Derived.** `n_private / n_facilities` — share of for-profit facilities (0–1) |
| `supply_change` | float | **Derived.** `n_residential (current year) − n_residential (2019)` — net change in residential facilities since 2019 |

**Known nulls** (expected, not data quality issues):
`mmm_code`, `quality_score`, `access_rate`, `care_gap_index` ≈ 2.1% (≈ 7 SA3s with no ACQSC-rated facility);
`total_residential` ≈ 2.1% (SA3s with no residential facility);
`waitlist_pressure` ≈ 0.9% (SA3s with `residential_places = 0`);
`supply_change` ≈ 0.9% (SA3s not present in the 2019 baseline).

---

## Derived metrics — formulas in one place

| Metric | Formula | Grain | Used in |
|---|---|---|---|
| `quality_score` | mean(`residents_exp`, `staffing`, `compliance`, `quality_measures`) | facility × snapshot, averaged to SA3 × year | All chapters |
| `access_rate` | `total_residential / pop_65_plus × 100` | SA3 × year | Ch 1 map, KPIs |
| `care_gap_index` | `access_rate / quality_score` | SA3 × year | **Ch 1 headline metric**, Ch 2 |
| `waitlist_pressure` | `hcp_high_needs / residential_places` | SA3 × year | Ch 3 reveal |
| `beds_per_1k` | `residential_places / pop_65_plus × 1000` | SA3 × year | Ch 1 supply trend |
| `private_share` | `n_private / n_facilities` | SA3 × year | Ch 2 ownership |
| `supply_change` | `n_residential − n_residential[2019]` | SA3 × year | Ch 1 supply collapse |
| `hcp_high_needs` | `hcp_level3 + hcp_level4` | SA3 × year | Ch 3 |

---

## 01 — `star_ratings_by_facility.csv`

**Source notebook:** `notebooks/clean_pipeline/01_treat_star_ratings.ipynb`
**Raw source:** ACQSC quarterly Star Ratings extracts, 12 files (`data/raw/star_ratings/star-ratings-quarterly-data-extract-*.xlsx`)
**Grain:** one row per **facility × quarterly snapshot** (May 2023 → Feb 2026; 12 snapshots)
**Rows:** 31,177 · **Columns:** 24

| Column | Type | Description |
|---|---|---|
| `snapshot` | str | Snapshot label (e.g. `"February 2026"`) |
| `snapshot_date` | datetime | First day of snapshot month |
| `Service Name` | str | Facility name |
| `Provider Name` | str | Provider (parent organisation) |
| `Purpose` | str | Raw ownership label (`Private Incorporated Body`, `Religious`, etc.) |
| `state` | str | State / territory |
| `acpr_name` | str | ACPR region name |
| `mmm_code` | str | MMM remoteness band (MM1–MM7) |
| `mmm_region` | str | MMM region name |
| `overall_rating` | float | ACQSC overall star rating (1–5) |
| `residents_exp` | float | Residents' experience sub-rating |
| `compliance` | float | Compliance sub-rating |
| `staffing` | float | Staffing sub-rating |
| `quality_measures` | float | Quality measures sub-rating |
| `quality_score` | float | **Mean of the 4 sub-ratings above — headline quality metric** |
| `rn_minutes_target` | float | Registered Nurse minutes / resident / day target (regulator-set) |
| `rn_minutes_actual` | float | RN minutes / resident / day actually delivered |
| `total_minutes_target` | float | Total care-minutes target |
| `total_minutes_actual` | float | Total care-minutes delivered |
| `rn_compliant` | bool/str | Whether facility met its RN-minutes target |
| `total_compliant` | bool/str | Whether facility met its total-minutes target |
| `fully_compliant` | bool/str | Met both targets — used in Ch 4 compliance trend |
| `sa3_code` | float | SA3 code (linked from facility postcode) |
| `sa3_name` | str | SA3 name |

---

## 02 — `service_supply_by_sa3.csv`

**Source notebook:** `notebooks/clean_pipeline/02_treat_service_list.ipynb`
**Raw source:** AIHW GEN Aged Care Service List, 7 annual snapshots (`data/raw/service_list/Australia*.xlsx`, 2019 → 2025)
**Grain:** one row per **SA3 × year** (2019–2025)
**Rows:** 2,307

| Column | Type | Description |
|---|---|---|
| `sa3_code` | float | SA3 region code |
| `sa3_name` | str | SA3 region name |
| `year` | int | Calendar year |
| `n_facilities` | int | Total aged-care services in the SA3 |
| `n_residential` | int | Residential-care services (incl. multi-purpose) |
| `n_homecare` | int | Home-care services (incl. multi-purpose) |
| `residential_places` | float | Licensed residential beds |
| `homecare_places` | float | Approved home-care packages |
| `n_nfp` | int | Facilities run by not-for-profit orgs |
| `n_government` | int | Facilities run by government |
| `n_private` | int | Facilities run by for-profit orgs |

---

## 03 — `service_users_by_sa3.csv`

**Source notebook:** `notebooks/clean_pipeline/03_treat_service_users_snapshots.ipynb`
**Raw source:** AIHW GEN "People using aged care by region" SA3 snapshots, 3 years × 3 tables each — residential, home-care (recipient-location), home-care (service-location) — at `data/raw/service_users_snapshot_SA3/GEN-data-*.xlsx`
**Grain:** one row per **SA3 × year**, point-in-time count at 30 June (2023–2025)
**Rows:** 1,005

| Column | Type | Description |
|---|---|---|
| `sa3_code` | float | SA3 region code |
| `sa3_name` | str | SA3 region name |
| `year` | int | Snapshot year (2023, 2024, 2025) |
| `permanent` | float | Permanent residential-care users |
| `respite` | float | Respite residential-care users |
| `total_residential` | float | Total residential users |
| `hcp_level1` | int | HCP Level 1 users (basic) |
| `hcp_level2` | int | HCP Level 2 users (moderate) |
| `hcp_level3` | int | HCP Level 3 users (high) |
| `hcp_level4` | int | HCP Level 4 users (very high) |
| `total_homecare` | int | Total home-care users |
| `total_users` | float | All aged-care users |
| `hcp_high_needs` | int | `hcp_level3 + hcp_level4` — proxy for residential-bed pressure |
| `pct_hcp_high` | float | `hcp_high_needs / total_homecare` — share of HCP users in L3/L4 |

---

## 04 — `homecare_admissions_by_acpr.csv`

**Source notebook:** `notebooks/clean_pipeline/04_treat_admissions_homecare.ipynb` (Part 1)
**Raw source:** AIHW CURF `data/raw/admission/CURF_Admissions-into-aged-care_2023-24.xlsx` + GEN aggregates `Admissionshomecare_2019–20_GENdata.xlsx`, `…2020–21_GENdata.xlsx`
**Grain:** one row per **ACPR × year** (2020–2024). **SA3 not available** in CURF admission records — ACPR is the finest geography
**Rows:** 73 ACPRs × 5 years

| Column | Type | Description |
|---|---|---|
| `acpr_code` | str | ACPR region code |
| `acpr_name` | str | ACPR region name |
| `state` | str | State / territory |
| `year` | int | Financial-year end (e.g. 2020 = FY 2019–20) |
| `n_first_admission` | int | New admissions (first home-care episode) |
| `n_repeat_admission` | int | Repeat admissions |
| `hcp_l1` – `hcp_l4` | int | Admissions by HCP level |
| `n_age_0_49` … `n_age_100_plus` | int | Admissions by 5-year age band |
| `n_male`, `n_female` | int | Admissions by sex |
| `n_indigenous` | int | Indigenous admissions |
| `n_nesb` | int | Non-English speaking background |
| `n_english_speaking` | int | English-speaking background |

---

## 05 — `home_care_users_by_acpr.csv`

**Source notebook:** `notebooks/clean_pipeline/04_treat_admissions_homecare.ipynb` (Part 2)
**Raw source:** AIHW CURF `service_users_CURF/CURF_People-using_aged_care-2024.xlsx`, GEN aggregates `service_users_CURF/People-using-aged-care-services-30-June-2020.xlsx`, `…30-June-2023.xlsx`
**Grain:** one row per **ACPR × year** (2018–2024). 2018–2019 rows come from pre-aggregated GEN data
**Rows:** 73 ACPRs × 7 years

| Column | Type | Description |
|---|---|---|
| `acpr_code` | float | ACPR region code |
| `acpr_name` | str | ACPR region name |
| `state` | str | State / territory |
| `year` | int | Year |
| `total_users` | int | Total home-care users |
| `hcp_l1` – `hcp_l4` | int | Users by HCP level |
| `n_age_0_49` … `n_age_100_plus` | int | Users by 5-year age band |
| `n_male`, `n_female` | int | Users by sex |
| `n_indigenous` | int | Indigenous users |
| `n_nesb` | int | Non-English speaking background |
| `n_english_speaking` | int | English-speaking background |

---

## 06 — `residential_admissions_by_acpr.csv`

**Source notebook:** `notebooks/clean_pipeline/05_treat_residential.ipynb` (Part 1)
**Raw source:** Same CURF admission file as File 04 + GEN aggregates `admission/Admissionsresidential_2019–20_GENdata.xlsx`, `…2020–21_GENdata.xlsx`
**Grain:** one row per **ACPR × year** (2020–2024)
**Rows:** 73 ACPRs × 5 years

| Column | Type | Description |
|---|---|---|
| `acpr_code` | int | ACPR region code |
| `acpr_name` | str | ACPR region name |
| `state` | str | State / territory |
| `year` | int | Financial-year end |
| `n_permanent` | int | Permanent residential admissions |
| `n_respite` | int | Respite residential admissions |
| `n_first_admission` | int | First-time admissions |
| `n_repeat_admission` | int | Repeat admissions |
| `n_age_0_49` … `n_age_100_plus` | int | Admissions by 5-year age band |
| `n_male`, `n_female` | int | Admissions by sex |
| `n_indigenous` | int | Indigenous admissions |
| `n_nesb` | int | Non-English speaking background |
| `n_english_speaking` | int | English-speaking background |

---

## 07 — `residential_users_by_acpr.csv`

**Source notebook:** `notebooks/clean_pipeline/05_treat_residential.ipynb` (Part 2)
**Raw source:** Same CURF service-user files as File 05
**Grain:** one row per **ACPR × year** (2018–2024)
**Rows:** 73 ACPRs × 7 years

| Column | Type | Description |
|---|---|---|
| `acpr_code` | float | ACPR region code |
| `acpr_name` | str | ACPR region name |
| `state` | str | State / territory |
| `year` | int | Year |
| `total_users` | int | Total residential-care users |
| `n_permanent` | int | Permanent care users |
| `n_respite` | int | Respite care users |
| `n_age_0_49` … `n_age_100_plus` | int | Users by 5-year age band |
| `n_male`, `n_female` | int | Users by sex |
| `n_indigenous` | int | Indigenous users |
| `n_nesb` | int | Non-English speaking background |
| `n_english_speaking` | int | English-speaking background |

---

## 08 — `service_funding_by_facility.csv`

**Source notebook:** `notebooks/clean_pipeline/06_treat_service_funding.ipynb`
**Raw source:** AIHW GEN service-level subsidy / funding extract (joined back to the AIHW service-list facility key — same join as File 02)
**Grain:** one row per **facility × year** (years with funding data: 2019–2022, 2024–2025)
**Rows:** 37,733

| Column | Type | Description |
|---|---|---|
| `service_name` | str | Facility name |
| `sa3_code` | float | SA3 region code |
| `sa3_name` | str | SA3 region name |
| `state` | str | State / territory |
| `care_type` | str | Type of care delivered (`Residential` / `Home Care` / etc.) |
| `org_type` | str | Normalised ownership: `profit` / `not_for_profit` / `government` |
| `year` | int | Financial-year end |
| `funding` | float | Australian Government funding ($AUD). **Negative values = clawback / reconciliation adjustments** (kept as-is — drop them per-analysis if needed) |

---

## 09 — `abs_population_by_sa3.csv`

**Source notebook:** `notebooks/clean_pipeline/07_treat_abs_population.ipynb`
**Raw source:** ABS catalogue 3235.0 — `data/raw/abs_population/32350DS0005_2001-24.xlsx` (Table 3 — Persons)
**Grain:** one row per **SA3 × year**
**Year range:** 2019–2024 · **Rows:** 2,016 · **Unique SA3s:** 336

| Column | Type | Description |
|---|---|---|
| `sa3_code` | str | 5-digit SA3 code, integer string (e.g. `"10102"`) |
| `sa3_name` | str | SA3 name |
| `state` | str | State abbreviation (NSW, VIC, QLD, SA, WA, TAS, NT, ACT) |
| `year` | int | Calendar year (30 June reference date) |
| `total_pop` | float | Estimated resident population, all ages |
| `pop_65_plus` | float | Population aged 65+, sum of 5-year bands 65–69 through 85+ |

**Used for:** `access_rate`, `beds_per_1k`, `care_gap_index` denominators in `master_sa3.csv` and the 2025 forecast scenario in `tabs/utils.py:build_master_2025`.

---

## Manual override table — `data/manual/sa3_overrides.csv`

Not a pipeline output (lives outside `data/clean/`) but documented here for completeness because the clean pipeline reads it.

**Purpose:** when a facility's suburb maps to multiple SA3s — or to none — this table records the **canonical SA3** for that facility so the `groupby('sa3_code')` aggregations in the pipeline don't drop rows or split a facility across two regions.
**Grain:** one row per facility · **Rows:** 77

| Column | Type | Description |
|---|---|---|
| `service_name` | str | Facility name (matches `Service Name` in File 01) |
| `service_suburb` | str | Suburb on the facility's address line |
| `state` | str | State / territory |
| `sa3_code` | float | Assigned SA3 code |
| `sa3_name` | str | Assigned SA3 name |
| `match_status` | str | How the assignment was resolved: `matched`, `matched_via_alias`, `matched_dominant`, `matched_dominant_via_alias` |
| `dominance` | float | When the suburb mapped to multiple SA3s, the share of population in the chosen SA3 (0–1) |
| `n_sa3` | float | How many SA3s the suburb originally mapped to |

---

## Geographic units

| Unit | Count | Used in |
|---|---|---|
| SA3 | 330 in `master_sa3.csv`, ≈ 336 in raw ABS | Files 00, 01, 02, 03, 08, 09 — main join key for dashboard |
| ACPR | 73 regions | Files 04, 05, 06, 07 — demographics only (CURF limitation: SA3 not available in admission CURF) |
| MMM | MM1 (major city) → MM7 (very remote) | File 01 facility-level + File 00 SA3-level (mode of facility MMMs) |

**Excluded SA3:** `10702 — Illawarra Catchment Reserve` (conservation land, `pop_65_plus = 0`).
All ratio metrics would be undefined → removed in `notebooks/architect/02_metrics.ipynb`.
