# Clean Data — File Dictionary

All files in this folder are outputs of the clean pipeline (`notebooks/clean_pipeline/`).
**Do not edit manually.** Re-run the corresponding notebook to regenerate.

---

## 01 — `star_ratings_by_facility.csv`
**Notebook:** `01_treat_star_ratings.ipynb`
**Grain:** one row per facility × quarter (2023 Q2 → 2026 Q1)

| Column | Description |
|--------|-------------|
| `sa3_code`, `sa3_name` | SA3 region (2016 boundaries) |
| `state` | State/territory |
| `mmm_code` | Modified Monash Model remoteness (MM1=major city → MM7=very remote) |
| `year`, `quarter` | Time period |
| `overall_rating` | Overall star rating (1–5) |
| `residents_exp` | Residents' experience star rating |
| `staffing` | Staffing star rating |
| `compliance` | Compliance star rating |
| `quality_measures` | Quality measures star rating |
| `quality_score` | Mean of the 4 sub-ratings above — headline quality metric |

---

## 02 — `service_supply_by_sa3.csv`
**Notebook:** `02_treat_service_list.ipynb`
**Grain:** one row per SA3 × year (2019–2025)

| Column | Description |
|--------|-------------|
| `sa3_code`, `sa3_name` | SA3 region |
| `year` | Year (2019–2025) |
| `n_facilities` | Total aged care services in the SA3 |
| `n_residential` | Number of residential care services (incl. multi-purpose) |
| `n_homecare` | Number of home care services (incl. multi-purpose) |
| `residential_places` | Licensed residential beds |
| `homecare_places` | Approved home care packages |
| `n_nfp` | Facilities run by not-for-profit orgs (Charitable, Religious, Community Based) |
| `n_government` | Facilities run by government (State, Local, Territory) |
| `n_private` | Facilities run by for-profit orgs (Private Incorporated Body, Publicly Listed) |

---

## 03 — `service_users_by_sa3.csv`
**Notebook:** `03_treat_service_users_snapshots.ipynb`
**Grain:** one row per SA3 × year (2023–2025), point-in-time count as at 30 June

| Column | Description |
|--------|-------------|
| `sa3_code`, `sa3_name` | SA3 region |
| `year` | Snapshot year (2023, 2024, 2025) |
| `permanent` | Permanent residential care users |
| `respite` | Respite residential care users |
| `total_residential` | Total residential users |
| `hcp_level1`–`hcp_level4` | Home care users by HCP level |
| `total_homecare` | Total home care users |
| `total_users` | All aged care users |
| `hcp_high_needs` | Level 3 + Level 4 users — proxy for residential waitlist pressure |
| `pct_hcp_high` | `hcp_high_needs / total_homecare` |

---

## 04 — `homecare_admissions_by_acpr.csv`
**Notebook:** `04_treat_admissions_homecare.ipynb` — Part 1
**Grain:** one row per ACPR × year (2020–2024)
**Note:** ACPR level only — SA3 not available in CURF admission records

| Column | Description |
|--------|-------------|
| `acpr_code`, `acpr_name`, `state` | ACPR region (73 regions nationally) |
| `year` | Financial year end (2020 = FY 2019–20) |
| `n_first_admission` | New admissions (first time in home care) |
| `n_repeat_admission` | Repeat admissions |
| `hcp_l1`–`hcp_l4` | Admissions by HCP level |
| `n_age_*` | Admissions by age bracket (0–49, 50–54, … 95–99, 100+) |
| `n_male`, `n_female` | Admissions by sex |
| `n_indigenous` | Indigenous admissions |
| `n_nesb` | Non-English speaking background |
| `n_english_speaking` | English-speaking background |

---

## 05 — `home_care_users_by_acpr.csv`
**Notebook:** `04_treat_admissions_homecare.ipynb` — Part 2
**Grain:** one row per ACPR × year (2018–2024)
**Note:** CURF individual-level records; 2018–2019 file is pre-aggregated GEN data

| Column | Description |
|--------|-------------|
| `acpr_code`, `acpr_name`, `state` | ACPR region |
| `year` | Year |
| `total_users` | Total home care users |
| `hcp_l1`–`hcp_l4` | Users by HCP level |
| `n_age_*` | Users by age bracket |
| `n_male`, `n_female` | Users by sex |
| `n_indigenous` | Indigenous users |
| `n_nesb` | Non-English speaking background |
| `n_english_speaking` | English-speaking background |

---

## 06 — `residential_admissions_by_acpr.csv`
**Notebook:** `05_treat_residential.ipynb` — Part 1
**Grain:** one row per ACPR × year (2020–2024)

| Column | Description |
|--------|-------------|
| `acpr_code`, `acpr_name`, `state` | ACPR region |
| `year` | Financial year end |
| `n_permanent` | Permanent residential admissions |
| `n_respite` | Respite residential admissions |
| `n_first_admission` | First-time admissions |
| `n_repeat_admission` | Repeat admissions |
| `n_age_*` | Admissions by age bracket |
| `n_male`, `n_female` | Admissions by sex |
| `n_indigenous` | Indigenous admissions |
| `n_nesb` | Non-English speaking background |
| `n_english_speaking` | English-speaking background |

---

## 07 — `residential_users_by_acpr.csv`
**Notebook:** `05_treat_residential.ipynb` — Part 2
**Grain:** one row per ACPR × year (2018–2024)

| Column | Description |
|--------|-------------|
| `acpr_code`, `acpr_name`, `state` | ACPR region |
| `year` | Year |
| `total_users` | Total residential care users |
| `n_permanent` | Permanent care users |
| `n_respite` | Respite care users |
| `n_age_*` | Users by age bracket |
| `n_male`, `n_female` | Users by sex |
| `n_indigenous` | Indigenous users |
| `n_nesb` | Non-English speaking background |
| `n_english_speaking` | English-speaking background |

---

## 08 — `service_funding_by_facility.csv`
**Notebook:** `06_treat_service_funding.ipynb`
**Grain:** one row per facility × year (years where funding data available: 2019–2022, 2024–2025)

| Column | Description |
|--------|-------------|
| `service_name` | Facility name |
| `sa3_code`, `sa3_name`, `state` | SA3 region |
| `care_type` | Type of care delivered |
| `org_type` | `profit` / `not_for_profit` / `government` |
| `year` | Financial year end |
| `funding` | Australian Government funding ($AUD). Negative values = clawback/reconciliation adjustments |

---

## 09 — `abs_population_by_sa3.csv`

**Source notebook:** `notebooks/clean_pipeline/07_treat_abs_population.ipynb`  
**Source raw file:** `data/raw/abs_population/32350DS0005_2001-24.xlsx` (Table 3 — Persons)  
**Grain:** one row per SA3 × year  
**Year range:** 2019–2024  
**Rows:** 2,016 | **Unique SA3s:** 336

| Column | Type | Description |
|--------|------|-------------|
| `sa3_code` | str | 5-digit SA3 code, integer string (e.g. `"10102"`) |
| `sa3_name` | str | SA3 name |
| `state` | str | State abbreviation (NSW, VIC, QLD, SA, WA, TAS, NT, ACT) |
| `year` | int | Calendar year (30 June reference date) |
| `total_pop` | float | Estimated resident population, all ages |
| `pop_65_plus` | float | Population aged 65+, sum of 5-year bands 65–69 through 85+ |

**Used for:** `access_rate`, `beds_per_1000_elderly`, `care_gap_index` (computed in architect notebooks)

---

## Geographic units

| Unit | Count | Used in |
|------|-------|---------|
| SA3 | ~331–359 regions | Files 02, 03, 08, 09 — main join key for dashboard |
| ACPR | 73 regions | Files 04, 05, 06, 07 — demographics only (CURF limitation) |
| MMM | MM1–MM7 | File 01 — remoteness classification |
