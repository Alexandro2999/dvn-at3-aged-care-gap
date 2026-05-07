"""
Clean Pipeline — DVN AT3 Aged Care Gap
Converts raw data → 9 clean CSVs in data/clean/

Usage (run from project root):
    python notebooks/clean_pipeline/run_pipeline.py

Or from anywhere:
    python "C:/path/to/dvn-at3-aged-care-gap/notebooks/clean_pipeline/run_pipeline.py"
"""

import pandas as pd
import numpy as np
import os
import re
import sys

# ── Resolve project root regardless of where script is called from ──────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))

RAW   = os.path.join(PROJECT_ROOT, 'data', 'raw')
CLEAN = os.path.join(PROJECT_ROOT, 'data', 'clean')
MANUAL = os.path.join(PROJECT_ROOT, 'data', 'manual')

os.makedirs(CLEAN, exist_ok=True)

def sep(title):
    print(f'\n{"="*60}')
    print(f'  {title}')
    print(f'{"="*60}')

def check_raw_folder(name):
    path = os.path.join(RAW, name)
    if not os.path.exists(path):
        print(f'  ERROR: {path} not found')
        return False
    files = [f for f in os.listdir(path) if not f.startswith('~') and not f.startswith('.')]
    print(f'  {name}: {len(files)} files found')
    return True

# ── Pre-flight: check all raw folders exist ──────────────────────────────────
sep('Pre-flight check')
folders_needed = [
    'star_ratings', 'service_list', 'service_users_snapshot_SA3',
    'admission', 'service_users_CURF', 'abs_population', 'abs_geography'
]
all_ok = True
for folder in folders_needed:
    ok = check_raw_folder(folder)
    all_ok = all_ok and ok

if not all_ok:
    print('\nSome raw folders missing. Check your data/raw/ directory.')
    sys.exit(1)

print('\nAll raw folders present. Starting pipeline...')


# ─────────────────────────────────────────────────────────────────────────────
# 01 — Star Ratings
# ─────────────────────────────────────────────────────────────────────────────
sep('01 — Star Ratings → star_ratings_by_facility.csv')

RAW_STARS   = os.path.join(RAW, 'star_ratings')
RAW_SERVICE = os.path.join(RAW, 'service_list')
OUT_01      = os.path.join(CLEAN, 'star_ratings_by_facility.csv')

MONTH_MAP = {
    'January':1,'February':2,'March':3,'April':4,
    'May':5,'June':6,'July':7,'August':8,
    'September':9,'October':10,'November':11,'December':12
}

# Load and combine all 12 snapshots
frames = []
for fname in sorted(os.listdir(RAW_STARS)):
    if not fname.endswith('.xlsx') or fname.startswith('~$'):
        continue
    path = os.path.join(RAW_STARS, fname)
    xl   = pd.ExcelFile(path, engine='calamine')
    sheets = xl.sheet_names
    if 'Detailed data' in sheets:
        sheet = 'Detailed data'
    else:
        sheet = next(s for s in sheets if 'Star' in s or 'star' in s)
    df = pd.read_excel(path, sheet_name=sheet, engine='calamine')
    df['source_file'] = fname
    frames.append(df)

stars = pd.concat(frames, ignore_index=True)
print(f'Combined: {stars.shape}  |  snapshots: {stars["Reporting Period"].nunique()}')

# Rename columns
stars = stars.rename(columns={
    'Reporting Period'                          : 'snapshot',
    'State/Territory'                           : 'state',
    'Aged Care Planning Region'                 : 'acpr_name',
    'MMM Code'                                  : 'mmm_code',
    'MMM Region'                                : 'mmm_region',
    'Overall Star Rating'                       : 'overall_rating',
    "Residents' Experience rating"              : 'residents_exp',
    'Staffing rating'                           : 'staffing',
    'Compliance rating'                         : 'compliance',
    'Quality Measures rating'                   : 'quality_measures',
    '[S] Registered Nurse Care Minutes - Target': 'rn_minutes_target',
    '[S] Registered Nurse Care Minutes - Actual': 'rn_minutes_actual',
    '[S] Total Care Minutes - Target'           : 'total_minutes_target',
    '[S] Total Care Minutes - Actual'           : 'total_minutes_actual',
})

# Fix January 2025 → February 2025 (known data issue in source file)
stars['snapshot'] = stars.apply(
    lambda r: 'February 2025'
    if r['snapshot'] == 'January 2025' and 'february-2025' in str(r['source_file'])
    else r['snapshot'], axis=1
)

# Numeric ratings
for c in ['residents_exp','staffing','compliance','quality_measures','overall_rating']:
    stars[c] = pd.to_numeric(stars[c], errors='coerce')

stars['quality_score'] = stars[['residents_exp','staffing','compliance','quality_measures']].mean(axis=1)

def parse_snapshot(s):
    parts = str(s).split()
    return pd.Timestamp(year=int(parts[1]), month=MONTH_MAP[parts[0]], day=1)

stars['snapshot_date'] = stars['snapshot'].apply(parse_snapshot)

for col in ['rn_minutes_target','rn_minutes_actual','total_minutes_target','total_minutes_actual']:
    if col in stars.columns:
        stars[col] = pd.to_numeric(stars[col], errors='coerce')
    else:
        stars[col] = pd.NA

has_rn    = stars['rn_minutes_target'].notna() & (stars['rn_minutes_target'] > 0) & stars['rn_minutes_actual'].notna()
has_total = stars['total_minutes_target'].notna() & (stars['total_minutes_target'] > 0) & stars['total_minutes_actual'].notna()
stars['rn_compliant']    = (stars['rn_minutes_actual'] >= stars['rn_minutes_target']).where(has_rn)
stars['total_compliant'] = (stars['total_minutes_actual'] >= stars['total_minutes_target']).where(has_total)
stars['fully_compliant'] = (
    (stars['rn_minutes_actual'] >= stars['rn_minutes_target']) &
    (stars['total_minutes_actual'] >= stars['total_minutes_target'])
).where(has_rn & has_total)

# SA3 lookup via service list (2025 → 2024 → 2023 fallback)
def build_sa3_lookup(year):
    fname = next(f for f in sorted(os.listdir(RAW_SERVICE))
                 if str(year) in f and not f.startswith('~'))
    path  = os.path.join(RAW_SERVICE, fname)
    probe = pd.read_excel(path, header=None, nrows=6, engine='calamine')
    hdr   = next(i for i, r in probe.iterrows() if 'Service Name' in str(list(r.values)))
    sl    = pd.read_excel(path, header=hdr, engine='calamine')
    sa3_col      = next(c for c in sl.columns if 'SA3 Code' in str(c))
    sa3_name_col = next(c for c in sl.columns if 'SA3 Name' in str(c))
    return (sl[['Service Name', sa3_col, sa3_name_col]]
            .drop_duplicates('Service Name')
            .rename(columns={sa3_col:'sa3_code', sa3_name_col:'sa3_name'}))

lookups = {yr: build_sa3_lookup(yr) for yr in [2025, 2024, 2023]}
stars = stars.merge(lookups[2025], on='Service Name', how='left')
for yr in [2024, 2023]:
    mask = stars['sa3_code'].isna()
    fill = stars.loc[mask, ['Service Name']].merge(lookups[yr], on='Service Name', how='left')
    stars.loc[mask, 'sa3_code'] = fill['sa3_code'].values
    stars.loc[mask, 'sa3_name'] = fill['sa3_name'].values
print(f'After service-list join: {stars["sa3_code"].notna().mean()*100:.1f}% matched')

# Manual overrides
overrides_path = os.path.join(MANUAL, 'sa3_overrides.csv')
if os.path.exists(overrides_path):
    overrides = pd.read_csv(overrides_path)
    override_map = {r['service_name']: (r['sa3_code'], r['sa3_name'])
                    for _, r in overrides.iterrows() if pd.notna(r['sa3_code'])}
    mask = stars['sa3_code'].isna() & stars['Service Name'].isin(override_map)
    for name, (code, sname) in override_map.items():
        nm = mask & (stars['Service Name'] == name)
        stars.loc[nm, 'sa3_code'] = code
        stars.loc[nm, 'sa3_name'] = sname
    print(f'After manual overrides: {stars["sa3_code"].notna().mean()*100:.2f}% matched')

unmapped = stars['sa3_code'].isna()
stars.loc[unmapped, 'sa3_code'] = -1
stars.loc[unmapped, 'sa3_name'] = 'UNMAPPED'

# Dedup and select columns
stars = stars.drop_duplicates(subset=['snapshot','Service Name','state','acpr_name'], keep='first')
keep_cols = ['snapshot','snapshot_date','Service Name','Provider Name','Purpose',
             'state','acpr_name','mmm_code','mmm_region',
             'overall_rating','residents_exp','compliance','staffing','quality_measures','quality_score',
             'rn_minutes_target','rn_minutes_actual','total_minutes_target','total_minutes_actual',
             'rn_compliant','total_compliant','fully_compliant','sa3_code','sa3_name']
stars = stars[[c for c in keep_cols if c in stars.columns]]
stars.to_csv(OUT_01, index=False)
print(f'✅ Saved: {stars.shape} → star_ratings_by_facility.csv')


# ─────────────────────────────────────────────────────────────────────────────
# 02 — Service List → service_supply_by_sa3.csv
# ─────────────────────────────────────────────────────────────────────────────
sep('02 — Service List → service_supply_by_sa3.csv')

OUT_02 = os.path.join(CLEAN, 'service_supply_by_sa3.csv')

def read_service_list(filepath):
    probe   = pd.read_excel(filepath, header=None, nrows=6, engine='calamine')
    hdr_row = next(i for i, r in probe.iterrows() if 'Service Name' in str(list(r.values)))
    return pd.read_excel(filepath, header=hdr_row, engine='calamine')

files = sorted([f for f in os.listdir(RAW_SERVICE) if not f.startswith('~')])
POSTCODE_COL = {2023:'Physical Post Code', 2024:'Postal Code', 2025:'Physical Post Code'}

# Build postcode → SA3 lookup
mapping_frames = []
for year in [2023, 2024, 2025]:
    fname = next(f for f in files if str(year) in f)
    df    = read_service_list(os.path.join(RAW_SERVICE, fname))
    sa3_col      = next(c for c in df.columns if 'SA3 Code' in str(c))
    sa3_name_col = next(c for c in df.columns if 'SA3 Name' in str(c))
    acpr_col     = next(c for c in df.columns if 'ACPR' in str(c) or 'Planning Region' in str(c))
    tmp = df[[POSTCODE_COL[year], acpr_col, sa3_col, sa3_name_col]].dropna()
    tmp.columns = ['postcode','acpr','sa3_code','sa3_name']
    tmp['postcode'] = tmp['postcode'].astype(str).str.strip().str.split('.').str[0]
    mapping_frames.append(tmp)

raw_mapping = pd.concat(mapping_frames, ignore_index=True)
pc_sa3_counts = raw_mapping.groupby('postcode')['sa3_code'].nunique()
unambiguous   = set(pc_sa3_counts[pc_sa3_counts == 1].index)
ambiguous     = set(pc_sa3_counts[pc_sa3_counts > 1].index)
postcode_sa3_simple = (raw_mapping[raw_mapping['postcode'].isin(unambiguous)]
                       .drop_duplicates('postcode')[['postcode','sa3_code','sa3_name']])
postcode_acpr_sa3   = (raw_mapping[raw_mapping['postcode'].isin(ambiguous)]
                       .groupby(['postcode','acpr','sa3_code','sa3_name']).size().reset_index(name='freq')
                       .sort_values('freq', ascending=False).drop_duplicates(['postcode','acpr'])
                       [['postcode','acpr','sa3_code','sa3_name']])
print(f'Lookup: {len(postcode_sa3_simple)} unambiguous + {len(postcode_acpr_sa3)} ambiguous combos')

NFP_TYPES  = {'charitable','religious','community based','religious/charitable'}
GOVT_TYPES = {'state government','local government','territory government'}
PRIV_TYPES = {'private incorporated body','publicly listed company'}

sa3_frames = []
for year in range(2019, 2026):
    fname = next(f for f in files if str(year) in f)
    df    = read_service_list(os.path.join(RAW_SERVICE, fname))
    has_sa3 = any('SA3 Code' in str(c) for c in df.columns)
    if has_sa3:
        sa3_col      = next(c for c in df.columns if 'SA3 Code' in str(c))
        sa3_name_col = next(c for c in df.columns if 'SA3 Name' in str(c))
        df = df.rename(columns={sa3_col:'sa3_code', sa3_name_col:'sa3_name'})
    else:
        acpr_col = next(c for c in df.columns if 'ACPR' in str(c) or 'Planning Region' in str(c))
        pc_col   = next(c for c in df.columns if 'Post Code' in str(c) or 'Postal Code' in str(c))
        df['postcode'] = df[pc_col].astype(str).str.strip().str.split('.').str[0]
        df = df.rename(columns={acpr_col:'acpr'})
        df = df.merge(postcode_sa3_simple, on='postcode', how='left')
        mask = df['sa3_code'].isna()
        if mask.sum() > 0:
            fill = df.loc[mask, ['postcode','acpr']].merge(postcode_acpr_sa3, on=['postcode','acpr'], how='left')
            df.loc[mask, 'sa3_code'] = fill['sa3_code'].values
            df.loc[mask, 'sa3_name'] = fill['sa3_name'].values

    care_col = next((c for c in df.columns if 'Care Type' in str(c)), None)
    if not care_col:
        continue
    df['is_residential'] = df[care_col].str.contains('Residential|Multi-Purpose', na=False, case=False).astype(int)
    df['is_homecare']    = df[care_col].str.contains('Home Care', na=False, case=False).astype(int)
    for col in ['Residential Places', 'Home Care Places']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0

    org_col = next((c for c in df.columns if 'Organisation' in str(c)), None)
    if org_col:
        org = df[org_col].astype(str).str.strip().str.lower()
        df['_nfp']     = org.isin(NFP_TYPES).astype(int)
        df['_govt']    = org.isin(GOVT_TYPES).astype(int)
        df['_private'] = org.isin(PRIV_TYPES).astype(int)
    else:
        df['_nfp'] = df['_govt'] = df['_private'] = 0

    agg = (df.dropna(subset=['sa3_code']).groupby(['sa3_code','sa3_name'])
           .agg(n_facilities=('Service Name','count'), n_residential=('is_residential','sum'),
                n_homecare=('is_homecare','sum'), residential_places=('Residential Places','sum'),
                homecare_places=('Home Care Places','sum'), n_nfp=('_nfp','sum'),
                n_government=('_govt','sum'), n_private=('_private','sum')).reset_index())
    agg['year'] = year
    sa3_frames.append(agg)
    print(f'  {year}: {len(agg)} SA3 regions')

supply_sa3 = pd.concat(sa3_frames, ignore_index=True)
supply_sa3.to_csv(OUT_02, index=False)
print(f'✅ Saved: {supply_sa3.shape} → service_supply_by_sa3.csv')


# ─────────────────────────────────────────────────────────────────────────────
# 03 — Service Users Snapshots → service_users_by_sa3.csv
# ─────────────────────────────────────────────────────────────────────────────
sep('03 — Service Users Snapshots → service_users_by_sa3.csv')

RAW_SNAP = os.path.join(RAW, 'service_users_snapshot_SA3')
OUT_03   = os.path.join(CLEAN, 'service_users_by_sa3.csv')

def valid_xlsx(f): return f.endswith('.xlsx') and not f.startswith('~$')

# Residential snapshots
res_files = sorted([f for f in os.listdir(RAW_SNAP)
                    if 'residential' in f and 'service-location' in f and valid_xlsx(f)])
res_frames = []
for fname in res_files:
    year = int(fname.split('June-')[1].split('-')[0])
    xl   = pd.ExcelFile(os.path.join(RAW_SNAP, fname), engine='calamine')
    sa3_sheet = next(s for s in xl.sheet_names if 'SA3' in s)
    df = pd.read_excel(os.path.join(RAW_SNAP, fname), sheet_name=sa3_sheet,
                       header=None, skiprows=3, engine='calamine')
    df.columns = ['sa3_code','sa3_name','permanent','respite','total_residential']
    df = df[pd.to_numeric(df['sa3_code'], errors='coerce').notna()].copy()
    for c in ['permanent','respite','total_residential']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['year'] = year
    res_frames.append(df)
    print(f'  Residential {year}: {len(df)} SA3s')

res = pd.concat(res_frames, ignore_index=True)

# Home care snapshots (recipient location)
hc_files = sorted([f for f in os.listdir(RAW_SNAP)
                   if 'home-care' in f and 'recipient' in f and valid_xlsx(f)])
hc_frames = []
for fname in hc_files:
    year = int(fname.split('June-')[1].split('-')[0])
    xl   = pd.ExcelFile(os.path.join(RAW_SNAP, fname), engine='calamine')
    sa3_sheet = next(s for s in xl.sheet_names if 'SA3' in s)
    df = pd.read_excel(os.path.join(RAW_SNAP, fname), sheet_name=sa3_sheet,
                       header=None, skiprows=3, engine='calamine')
    df.columns = ['sa3_code','sa3_name','hcp_level1','hcp_level2','hcp_level3','hcp_level4','total_homecare']
    df = df[pd.to_numeric(df['sa3_code'], errors='coerce').notna()].copy()
    for c in ['hcp_level1','hcp_level2','hcp_level3','hcp_level4','total_homecare']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['year'] = year
    hc_frames.append(df)
    print(f'  Home care {year}: {len(df)} SA3s')

hc = pd.concat(hc_frames, ignore_index=True)

access = res[['sa3_code','sa3_name','year','permanent','respite','total_residential']].merge(
    hc[['sa3_code','sa3_name','year','hcp_level1','hcp_level2','hcp_level3','hcp_level4','total_homecare']],
    on=['sa3_code','year'], how='outer', suffixes=('','_hc'))
access['sa3_name']      = access['sa3_name'].fillna(access['sa3_name_hc'])
access                   = access.drop(columns=['sa3_name_hc'])
access['total_users']   = access['total_residential'].fillna(0) + access['total_homecare'].fillna(0)
access['hcp_high_needs'] = access['hcp_level3'].fillna(0) + access['hcp_level4'].fillna(0)
access['pct_hcp_high']   = access['hcp_high_needs'] / access['total_homecare']
access['sa3_code']       = access['sa3_code'].astype(str).str.strip()
access.to_csv(OUT_03, index=False)
print(f'✅ Saved: {access.shape} → service_users_by_sa3.csv')


# ─────────────────────────────────────────────────────────────────────────────
# 04 — Admissions Home Care → homecare_admissions_by_acpr.csv + home_care_users_by_acpr.csv
# ─────────────────────────────────────────────────────────────────────────────
sep('04 — Admissions Home Care → homecare_admissions_by_acpr.csv + home_care_users_by_acpr.csv')

RAW_ADM   = os.path.join(RAW, 'admission')
RAW_CURF  = os.path.join(RAW, 'service_users_CURF')
OUT_HC_ADM  = os.path.join(CLEAN, 'homecare_admissions_by_acpr.csv')
OUT_HC_USR  = os.path.join(CLEAN, 'home_care_users_by_acpr.csv')

GROUP_COLS = ['acpr_code','acpr_name','state','year']
WANTED = {
    'ACPR_code','ACPR_CODE','ACPR_CODE_2018','ACPR_name','ACPR_NAME','ACPR_NAME_2018',
    'State','STATE','Year','YEAR','Financial_year','FINANCIAL_YEAR',
    'Care_type','CARE_TYPE','Admission_type','ADMISSION_TYPE',
    'First_admission','First _admission','FIRST_ADMISSION',
    'Age_group','AGE_GROUP','AGE_GROUP_5','Sex','SEX',
    'Indigenous_status','INDIGENOUS_STATUS','Country_of_birth','COUNTRY_OF_BIRTH','count',
}
COL_MAP = {
    'ACPR_code':'acpr_code','ACPR_CODE':'acpr_code','ACPR_CODE_2018':'acpr_code',
    'ACPR_name':'acpr_name','ACPR_NAME':'acpr_name','ACPR_NAME_2018':'acpr_name',
    'State':'state','STATE':'state',
    'Year':'year','YEAR':'year','Financial_year':'year','FINANCIAL_YEAR':'year',
    'Care_type':'care_type','CARE_TYPE':'care_type',
    'Admission_type':'admission_type','ADMISSION_TYPE':'admission_type',
    'First_admission':'first_admission','First _admission':'first_admission','FIRST_ADMISSION':'first_admission',
    'Age_group':'age_group','AGE_GROUP':'age_group','AGE_GROUP_5':'age_group',
    'Sex':'sex','SEX':'sex',
    'Indigenous_status':'indigenous_status','INDIGENOUS_STATUS':'indigenous_status',
    'Country_of_birth':'country_of_birth','COUNTRY_OF_BIRTH':'country_of_birth',
}
HC_TYPES = {'home care','home care package','hcp','community care','chsp','hacc','home care package program'}
AGE_MAP = {
    '0-49':'n_age_0_49','0–49':'n_age_0_49','50-54':'n_age_50_54','50–54':'n_age_50_54',
    '55-59':'n_age_55_59','55–59':'n_age_55_59','60-64':'n_age_60_64','60–64':'n_age_60_64',
    '65-69':'n_age_65_69','65–69':'n_age_65_69','70-74':'n_age_70_74','70–74':'n_age_70_74',
    '75-79':'n_age_75_79','75–79':'n_age_75_79','80-84':'n_age_80_84','80–84':'n_age_80_84',
    '85-89':'n_age_85_89','85–89':'n_age_85_89','90-94':'n_age_90_94','90–94':'n_age_90_94',
    '95-99':'n_age_95_99','95–99':'n_age_95_99','100+':'n_age_100_plus',
}
AGE_COLS = ['n_age_0_49','n_age_50_54','n_age_55_59','n_age_60_64','n_age_65_69',
            'n_age_70_74','n_age_75_79','n_age_80_84','n_age_85_89','n_age_90_94',
            'n_age_95_99','n_age_100_plus']
HCP_MAP = {
    'level 1':'hcp_l1','l1':'hcp_l1','1':'hcp_l1',
    'level 2':'hcp_l2','l2':'hcp_l2','2':'hcp_l2',
    'level 3':'hcp_l3','l3':'hcp_l3','3':'hcp_l3',
    'level 4':'hcp_l4','l4':'hcp_l4','4':'hcp_l4',
}
HCP_COLS = ['hcp_l1','hcp_l2','hcp_l3','hcp_l4']

def load_file(path):
    if path.endswith('.xlsx'):
        try:    return pd.read_excel(path, engine='calamine')
        except: return pd.read_excel(path)
    try:    return pd.read_csv(path, encoding='utf-8', low_memory=False)
    except: return pd.read_csv(path, encoding='latin1', low_memory=False)

def resolve_year(fname):
    m = re.search(r'20\d{2}[-–](\d{2})', fname)
    return int('20' + m.group(1)) if m else np.nan

def get_admt_series(df):
    if 'admission_type' in df.columns: return df['admission_type'].astype(str).str.strip().str.lower()
    if 'care_type' in df.columns:      return df['care_type'].astype(str).str.strip().str.lower()
    return pd.Series('', index=df.index)

def aggregate_hc_admissions(df, fname):
    keep = [c for c in df.columns if c in WANTED]
    df = df[keep].copy().rename(columns={k:v for k,v in COL_MAP.items() if k in df.columns})
    if 'acpr_code' not in df.columns: return None
    df['year'] = resolve_year(fname)
    df['acpr_code'] = df['acpr_code'].astype(str).str.strip()
    df = df[df['acpr_code'].str.len() > 0].dropna(subset=['acpr_code'])
    if df.empty: return None
    df['year'] = int(df['year'].iloc[0])
    if 'care_type' in df.columns:
        mask = df['care_type'].astype(str).str.strip().str.lower().isin(HC_TYPES)
        df = df[mask]
    if df.empty: return None
    gcols = [c for c in GROUP_COLS if c in df.columns]
    fa = df['first_admission'].astype(str).str.strip().str.lower() if 'first_admission' in df.columns else pd.Series('', index=df.index)
    df['_first']  = (fa == 'yes').astype(int)
    df['_repeat'] = (fa == 'no').astype(int)
    ind = df['indigenous_status'].astype(str).str.strip().str.lower() if 'indigenous_status' in df.columns else pd.Series('', index=df.index)
    df['_indigenous'] = (ind == 'indigenous').astype(int)
    sex = df['sex'].astype(str).str.strip().str.lower() if 'sex' in df.columns else pd.Series('', index=df.index)
    df['_male']   = sex.isin(['male','m','1']).astype(int)
    df['_female'] = sex.isin(['female','f','2']).astype(int)
    cob = df['country_of_birth'].astype(str).str.strip().str.lower() if 'country_of_birth' in df.columns else pd.Series('', index=df.index)
    df['_nesb']    = cob.str.contains('non-english', na=False).astype(int)
    df['_english'] = (cob.str.contains('english', na=False) & ~cob.str.contains('non-english', na=False)).astype(int)
    if 'age_group' in df.columns:
        age_norm = df['age_group'].astype(str).str.strip().map(AGE_MAP)
        for col in AGE_COLS: df[f'_{col}'] = (age_norm == col).astype(int)
    else:
        for col in AGE_COLS: df[f'_{col}'] = 0
    admt = get_admt_series(df)
    hcp_mapped = admt.map(HCP_MAP)
    for hcol in HCP_COLS: df[f'_{hcol}'] = (hcp_mapped == hcol).astype(int)
    agg_map = {
        'n_first_admission':('_first','sum'), 'n_repeat_admission':('_repeat','sum'),
        'n_indigenous':('_indigenous','sum'), 'n_male':('_male','sum'), 'n_female':('_female','sum'),
        'n_nesb':('_nesb','sum'), 'n_english_speaking':('_english','sum'),
    }
    for col in AGE_COLS: agg_map[col] = (f'_{col}', 'sum')
    for col in HCP_COLS: agg_map[col] = (f'_{col}', 'sum')
    return df.groupby(gcols).agg(**agg_map).reset_index()

results_hc_adm = []
for fname in sorted(os.listdir(RAW_ADM)):
    if fname.startswith('~') or not (fname.endswith('.xlsx') or fname.endswith('.csv')): continue
    path = os.path.join(RAW_ADM, fname)
    try:
        df  = load_file(path)
        agg = aggregate_hc_admissions(df, fname)
        if agg is not None:
            results_hc_adm.append(agg)
            print(f'  OK  {fname}: → {agg.shape}  year={agg["year"].iloc[0]}')
        del df
    except Exception as e:
        print(f'  ERR {fname}: {e}')

hc_adm = pd.concat(results_hc_adm, ignore_index=True)

# Backfill state
state_map = (hc_adm[hc_adm['state'].notna()][['acpr_code','state']]
             .drop_duplicates('acpr_code'))
hc_adm = hc_adm.merge(state_map.rename(columns={'state':'_sf'}), on='acpr_code', how='left')
hc_adm['state'] = hc_adm['state'].fillna(hc_adm['_sf'])
hc_adm = hc_adm.drop(columns=['_sf'])
hc_adm.to_csv(OUT_HC_ADM, index=False)
print(f'✅ Saved: {hc_adm.shape} → homecare_admissions_by_acpr.csv')

# Home care users (CURF)
WANTED_CURF = {
    'ACPR_code','ACPR_CODE','ACPR_CODE_2018','ACPR_name','ACPR_NAME','ACPR_NAME_2018',
    'State','STATE','Year','YEAR','Care_type','CARE_TYPE',
    'Age_group','AGE_GROUP','Sex','SEX','Indigenous_status','INDIGENOUS_STATUS',
    'Country_of_birth','COUNTRY_OF_BIRTH','count',
}

def aggregate_curf_hc(df, fname):
    keep = [c for c in df.columns if c in WANTED_CURF]
    df = df[keep].copy().rename(columns={k:v for k,v in COL_MAP.items() if k in df.columns})
    if 'acpr_code' not in df.columns: return None
    df['acpr_code'] = df['acpr_code'].astype(str).str.strip()
    df = df[df['acpr_code'].str.len() > 0].dropna(subset=['acpr_code'])
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year']); df['year'] = df['year'].astype(int)
    if 'care_type' in df.columns:
        mask = df['care_type'].astype(str).str.strip().str.lower().isin(HC_TYPES)
        df = df[mask]
    if df.empty: return None
    df['_weight'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int) if 'count' in df.columns else 1
    ind = df['indigenous_status'].astype(str).str.strip().str.lower() if 'indigenous_status' in df.columns else pd.Series('', index=df.index)
    df['_indigenous'] = ind.isin(['indigenous','1','2','3']).astype(int) * df['_weight']
    sex = df['sex'].astype(str).str.strip().str.lower() if 'sex' in df.columns else pd.Series('', index=df.index)
    df['_male']   = sex.isin(['male','males','1']).astype(int)    * df['_weight']
    df['_female'] = sex.isin(['female','females','2']).astype(int) * df['_weight']
    cob = df['country_of_birth'].astype(str).str.strip().str.lower() if 'country_of_birth' in df.columns else pd.Series('', index=df.index)
    df['_nesb']    = cob.str.contains('non-english', na=False).astype(int) * df['_weight']
    df['_english'] = (cob.str.contains('english', na=False) & ~cob.str.contains('non-english', na=False)).astype(int) * df['_weight']
    if 'age_group' in df.columns:
        age_norm = df['age_group'].astype(str).str.strip().map(AGE_MAP)
        for col in AGE_COLS: df[f'_{col}'] = (age_norm == col).astype(int) * df['_weight']
    else:
        for col in AGE_COLS: df[f'_{col}'] = 0
    admt = get_admt_series(df)
    hcp_mapped = admt.map(HCP_MAP)
    for hcol in HCP_COLS: df[f'_{hcol}'] = (hcp_mapped == hcol).astype(int) * df['_weight']
    gcols = [c for c in GROUP_COLS if c in df.columns]
    agg_map = {'total_users':('_weight','sum'),'n_indigenous':('_indigenous','sum'),
               'n_male':('_male','sum'),'n_female':('_female','sum'),
               'n_nesb':('_nesb','sum'),'n_english_speaking':('_english','sum')}
    for col in AGE_COLS: agg_map[col] = (f'_{col}','sum')
    for col in HCP_COLS: agg_map[col] = (f'_{col}','sum')
    return df.groupby(gcols).agg(**agg_map).reset_index()

results_hc_usr = []
for fname in sorted(os.listdir(RAW_CURF)):
    if fname.startswith('~') or not (fname.endswith('.xlsx') or fname.endswith('.csv')): continue
    path = os.path.join(RAW_CURF, fname)
    try:
        df  = load_file(path)
        agg = aggregate_curf_hc(df, fname)
        if agg is not None:
            results_hc_usr.append(agg)
            print(f'  OK  {fname}: → {agg.shape}  years={sorted(agg["year"].unique())}')
        del df
    except Exception as e:
        print(f'  ERR {fname}: {e}')

hc_usr = pd.concat(results_hc_usr, ignore_index=True)
hc_usr = hc_usr.merge(state_map.rename(columns={'state':'_sf'}), on='acpr_code', how='left')
hc_usr['state'] = hc_usr.get('state', pd.Series(dtype=str)).fillna(hc_usr['_sf'])
if 'state' not in hc_usr.columns: hc_usr['state'] = hc_usr['_sf']
hc_usr = hc_usr.drop(columns=['_sf'], errors='ignore')
hc_usr.to_csv(OUT_HC_USR, index=False)
print(f'✅ Saved: {hc_usr.shape} → home_care_users_by_acpr.csv')


# ─────────────────────────────────────────────────────────────────────────────
# 05 — Residential → residential_admissions_by_acpr.csv + residential_users_by_acpr.csv
# ─────────────────────────────────────────────────────────────────────────────
sep('05 — Residential → residential_admissions_by_acpr.csv + residential_users_by_acpr.csv')

OUT_RES_ADM  = os.path.join(CLEAN, 'residential_admissions_by_acpr.csv')
OUT_RES_USR  = os.path.join(CLEAN, 'residential_users_by_acpr.csv')

RESID_TYPES = {'permanent residential care','respite residential care','residential care','permanent','respite'}
ADMT_MAP = {
    'perm':'n_permanent','p':'n_permanent','permanent':'n_permanent','permanent residential care':'n_permanent',
    'resp':'n_respite','r':'n_respite','respite':'n_respite','respite residential care':'n_respite',
}
ADMT_COLS = ['n_permanent','n_respite']

def aggregate_res_admissions(df, fname):
    keep = [c for c in df.columns if c in WANTED]
    df = df[keep].copy().rename(columns={k:v for k,v in COL_MAP.items() if k in df.columns})
    if 'acpr_code' not in df.columns: return None
    df['year'] = resolve_year(fname)
    df['acpr_code'] = df['acpr_code'].astype(str).str.strip()
    df = df[df['acpr_code'].str.len() > 0].dropna(subset=['acpr_code'])
    if df.empty: return None
    df['year'] = int(df['year'].iloc[0])
    if 'care_type' in df.columns:
        mask = df['care_type'].astype(str).str.strip().str.lower().isin(RESID_TYPES)
        df = df[mask]
    if df.empty: return None
    gcols = [c for c in GROUP_COLS if c in df.columns]
    fa = df['first_admission'].astype(str).str.strip().str.lower() if 'first_admission' in df.columns else pd.Series('', index=df.index)
    df['_first']  = (fa == 'yes').astype(int)
    df['_repeat'] = (fa == 'no').astype(int)
    admt = get_admt_series(df)
    admt_mapped = admt.map(ADMT_MAP)
    df['_permanent'] = (admt_mapped == 'n_permanent').astype(int)
    df['_respite']   = (admt_mapped == 'n_respite').astype(int)
    ind = df['indigenous_status'].astype(str).str.strip().str.lower() if 'indigenous_status' in df.columns else pd.Series('', index=df.index)
    df['_indigenous'] = (ind == 'indigenous').astype(int)
    sex = df['sex'].astype(str).str.strip().str.lower() if 'sex' in df.columns else pd.Series('', index=df.index)
    df['_male']   = sex.isin(['male','m','1']).astype(int)
    df['_female'] = sex.isin(['female','f','2']).astype(int)
    cob = df['country_of_birth'].astype(str).str.strip().str.lower() if 'country_of_birth' in df.columns else pd.Series('', index=df.index)
    df['_nesb']    = cob.str.contains('non-english', na=False).astype(int)
    df['_english'] = (cob.str.contains('english', na=False) & ~cob.str.contains('non-english', na=False)).astype(int)
    if 'age_group' in df.columns:
        age_norm = df['age_group'].astype(str).str.strip().map(AGE_MAP)
        for col in AGE_COLS: df[f'_{col}'] = (age_norm == col).astype(int)
    else:
        for col in AGE_COLS: df[f'_{col}'] = 0
    agg_map = {
        'n_first_admission':('_first','sum'),'n_repeat_admission':('_repeat','sum'),
        'n_permanent':('_permanent','sum'),'n_respite':('_respite','sum'),
        'n_indigenous':('_indigenous','sum'),'n_male':('_male','sum'),'n_female':('_female','sum'),
        'n_nesb':('_nesb','sum'),'n_english_speaking':('_english','sum'),
    }
    for col in AGE_COLS: agg_map[col] = (f'_{col}','sum')
    return df.groupby(gcols).agg(**agg_map).reset_index()

results_res_adm = []
for fname in sorted(os.listdir(RAW_ADM)):
    if fname.startswith('~') or not (fname.endswith('.xlsx') or fname.endswith('.csv')): continue
    path = os.path.join(RAW_ADM, fname)
    try:
        df  = load_file(path)
        agg = aggregate_res_admissions(df, fname)
        if agg is not None:
            results_res_adm.append(agg)
            print(f'  OK  {fname}: → {agg.shape}  year={agg["year"].iloc[0]}')
        del df
    except Exception as e:
        print(f'  ERR {fname}: {e}')

res_adm = pd.concat(results_res_adm, ignore_index=True)
res_adm.to_csv(OUT_RES_ADM, index=False)
print(f'✅ Saved: {res_adm.shape} → residential_admissions_by_acpr.csv')

def aggregate_curf_resid(df, fname):
    keep = [c for c in df.columns if c in WANTED_CURF]
    df = df[keep].copy().rename(columns={k:v for k,v in COL_MAP.items() if k in df.columns})
    if 'acpr_code' not in df.columns: return None
    df['acpr_code'] = df['acpr_code'].astype(str).str.strip()
    df = df[df['acpr_code'].str.len() > 0].dropna(subset=['acpr_code'])
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year']); df['year'] = df['year'].astype(int)
    if 'care_type' in df.columns:
        mask = df['care_type'].astype(str).str.strip().str.lower().isin(RESID_TYPES)
        df = df[mask]
    if df.empty: return None
    df['_weight'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int) if 'count' in df.columns else 1
    admt = get_admt_series(df)
    admt_mapped = admt.map(ADMT_MAP)
    df['_permanent'] = (admt_mapped == 'n_permanent').astype(int) * df['_weight']
    df['_respite']   = (admt_mapped == 'n_respite').astype(int)   * df['_weight']
    ind = df['indigenous_status'].astype(str).str.strip().str.lower() if 'indigenous_status' in df.columns else pd.Series('', index=df.index)
    df['_indigenous'] = ind.isin(['indigenous','1','2','3']).astype(int) * df['_weight']
    sex = df['sex'].astype(str).str.strip().str.lower() if 'sex' in df.columns else pd.Series('', index=df.index)
    df['_male']   = sex.isin(['male','males','1']).astype(int)    * df['_weight']
    df['_female'] = sex.isin(['female','females','2']).astype(int) * df['_weight']
    cob = df['country_of_birth'].astype(str).str.strip().str.lower() if 'country_of_birth' in df.columns else pd.Series('', index=df.index)
    df['_nesb']    = cob.str.contains('non-english', na=False).astype(int) * df['_weight']
    df['_english'] = (cob.str.contains('english', na=False) & ~cob.str.contains('non-english', na=False)).astype(int) * df['_weight']
    if 'age_group' in df.columns:
        age_norm = df['age_group'].astype(str).str.strip().map(AGE_MAP)
        for col in AGE_COLS: df[f'_{col}'] = (age_norm == col).astype(int) * df['_weight']
    else:
        for col in AGE_COLS: df[f'_{col}'] = 0
    gcols = [c for c in GROUP_COLS if c in df.columns]
    agg_map = {'total_users':('_weight','sum'),'n_permanent':('_permanent','sum'),
               'n_respite':('_respite','sum'),'n_indigenous':('_indigenous','sum'),
               'n_male':('_male','sum'),'n_female':('_female','sum'),
               'n_nesb':('_nesb','sum'),'n_english_speaking':('_english','sum')}
    for col in AGE_COLS: agg_map[col] = (f'_{col}','sum')
    return df.groupby(gcols).agg(**agg_map).reset_index()

results_res_usr = []
for fname in sorted(os.listdir(RAW_CURF)):
    if fname.startswith('~') or not (fname.endswith('.xlsx') or fname.endswith('.csv')): continue
    path = os.path.join(RAW_CURF, fname)
    try:
        df  = load_file(path)
        agg = aggregate_curf_resid(df, fname)
        if agg is not None:
            results_res_usr.append(agg)
            print(f'  OK  {fname}: → {agg.shape}  years={sorted(agg["year"].unique())}')
        del df
    except Exception as e:
        print(f'  ERR {fname}: {e}')

res_usr = pd.concat(results_res_usr, ignore_index=True)
res_usr.to_csv(OUT_RES_USR, index=False)
print(f'✅ Saved: {res_usr.shape} → residential_users_by_acpr.csv')


# ─────────────────────────────────────────────────────────────────────────────
# 06 — Service Funding → service_funding_by_facility.csv
# ─────────────────────────────────────────────────────────────────────────────
sep('06 — Service Funding → service_funding_by_facility.csv')

OUT_06 = os.path.join(CLEAN, 'service_funding_by_facility.csv')
ORG_TYPE_MAP = {
    'private incorporated body':'profit','publicly listed company':'profit',
    'charitable':'not_for_profit','religious':'not_for_profit',
    'community based':'not_for_profit','religious/charitable':'not_for_profit',
    'state government':'government','local government':'government','territory government':'government',
}

def find_funding_col(df):
    return next((c for c in df.columns if 'funding' in str(c).lower()), None)

fund_frames = []
for year in range(2019, 2026):
    fname = next(f for f in files if str(year) in f)
    df    = read_service_list(os.path.join(RAW_SERVICE, fname))
    fund_col = find_funding_col(df)
    if not fund_col:
        print(f'  {year}: no funding column — skip')
        continue
    has_sa3 = any('SA3 Code' in str(c) for c in df.columns)
    if has_sa3:
        sa3_col      = next(c for c in df.columns if 'SA3 Code' in str(c))
        sa3_name_col = next(c for c in df.columns if 'SA3 Name' in str(c))
        df = df.rename(columns={sa3_col:'sa3_code', sa3_name_col:'sa3_name'})
    else:
        acpr_col = next(c for c in df.columns if 'ACPR' in str(c) or 'Planning Region' in str(c))
        pc_col   = next(c for c in df.columns if 'Post Code' in str(c) or 'Postal Code' in str(c))
        df['postcode'] = df[pc_col].astype(str).str.strip().str.split('.').str[0]
        df = df.rename(columns={acpr_col:'acpr'})
        df = df.merge(postcode_sa3_simple, on='postcode', how='left')
        mask = df['sa3_code'].isna()
        if mask.sum() > 0:
            fill = df.loc[mask, ['postcode','acpr']].merge(postcode_acpr_sa3, on=['postcode','acpr'], how='left')
            df.loc[mask, 'sa3_code'] = fill['sa3_code'].values
            df.loc[mask, 'sa3_name'] = fill['sa3_name'].values
    state_col = next((c for c in df.columns if c in {'Physical State','State','STATE'}), None)
    care_col  = next((c for c in df.columns if 'Care Type' in str(c)), None)
    org_col   = next((c for c in df.columns if 'Organisation' in str(c)), None)
    out = pd.DataFrame()
    out['service_name'] = df['Service Name']
    out['sa3_code']     = df['sa3_code']
    out['sa3_name']     = df['sa3_name']
    out['state']        = df[state_col] if state_col else np.nan
    out['care_type']    = df[care_col]  if care_col  else np.nan
    out['org_type']     = (df[org_col].astype(str).str.strip().str.lower().map(ORG_TYPE_MAP)
                           if org_col else np.nan)
    out['year']         = year
    out['funding']      = pd.to_numeric(df[fund_col], errors='coerce')
    out = out.dropna(subset=['sa3_code','funding'])
    fund_frames.append(out)
    print(f'  {year}: {len(out)} facilities | ${out["funding"].sum():,.0f}')

funding_result = pd.concat(fund_frames, ignore_index=True)
state_map_f = (funding_result[funding_result['state'].notna()][['sa3_code','state']]
               .drop_duplicates('sa3_code'))
funding_result = funding_result.merge(state_map_f.rename(columns={'state':'_sf'}), on='sa3_code', how='left')
funding_result['state'] = funding_result['state'].fillna(funding_result['_sf'])
funding_result = funding_result.drop(columns=['_sf'])
before = len(funding_result)
funding_result = (funding_result
                  .groupby(['service_name','sa3_code','sa3_name','state','care_type','org_type','year'], dropna=False)
                  ['funding'].sum().reset_index())
print(f'  Aggregated: {before} → {len(funding_result)} rows')
funding_result['sa3_code'] = funding_result['sa3_code'].astype(str).str.strip()
funding_result.to_csv(OUT_06, index=False)
print(f'✅ Saved: {funding_result.shape} → service_funding_by_facility.csv')


# ─────────────────────────────────────────────────────────────────────────────
# 07 — ABS Population → abs_population_by_sa3.csv
# ─────────────────────────────────────────────────────────────────────────────
sep('07 — ABS Population → abs_population_by_sa3.csv')

RAW_POP = os.path.join(RAW, 'abs_population')
OUT_07  = os.path.join(CLEAN, 'abs_population_by_sa3.csv')

pop_file = os.path.join(RAW_POP, '32350DS0005_2001-24.xlsx')
if not os.path.exists(pop_file):
    # Try to find it
    candidates = [f for f in os.listdir(RAW_POP) if f.endswith('.xlsx') and '32350' in f]
    if candidates:
        pop_file = os.path.join(RAW_POP, candidates[0])
    else:
        print(f'ERROR: Could not find ABS population file in {RAW_POP}')
        sys.exit(1)

YEARS = list(range(2019, 2025))
STATE_MAP = {1:'NSW',2:'VIC',3:'QLD',4:'SA',5:'WA',6:'TAS',7:'NT',8:'ACT'}
COLS = [
    'year','st_code','st_name','gccsa_code','gccsa_name',
    'sa4_code','sa4_name','sa3_code','sa3_name','sa2_code','sa2_name',
    'age_0_4','age_5_9','age_10_14','age_15_19','age_20_24',
    'age_25_29','age_30_34','age_35_39','age_40_44','age_45_49',
    'age_50_54','age_55_59','age_60_64',
    'age_65_69','age_70_74','age_75_79','age_80_84','age_85plus',
    'total_persons',
]

raw_pop = pd.read_excel(pop_file, sheet_name='Table 3', header=None, skiprows=7, engine='calamine')
raw_pop.columns = COLS
print(f'Loaded {len(raw_pop):,} rows')

df_pop = raw_pop[raw_pop['year'].isin(YEARS)].copy()
AGE_65_COLS = ['age_65_69','age_70_74','age_75_79','age_80_84','age_85plus']
df_pop['pop_65_plus'] = df_pop[AGE_65_COLS].sum(axis=1)
df_pop['state']       = df_pop['st_code'].map(STATE_MAP)
unmapped = df_pop['state'].isna().sum()
if unmapped > 0:
    print(f'  WARNING: {unmapped} rows with unmapped state code')

sa3 = (df_pop.groupby(['year','sa3_code','sa3_name','state'])[['total_persons','pop_65_plus']]
       .sum().reset_index().rename(columns={'total_persons':'total_pop'}))
sa3['sa3_code'] = pd.to_numeric(sa3['sa3_code'], errors='coerce').dropna().astype(int).astype(str)
sa3 = sa3[sa3['sa3_code'].notna()].copy()

out_pop = sa3[['sa3_code','sa3_name','state','year','total_pop','pop_65_plus']].sort_values(['sa3_code','year']).reset_index(drop=True)
out_pop.to_csv(OUT_07, index=False)
print(f'✅ Saved: {out_pop.shape} → abs_population_by_sa3.csv')


# ─────────────────────────────────────────────────────────────────────────────
# Final summary
# ─────────────────────────────────────────────────────────────────────────────
sep('Pipeline complete — Summary')

expected = {
    'star_ratings_by_facility.csv':         (31177, 24),
    'service_supply_by_sa3.csv':            (2307,  11),
    'service_users_by_sa3.csv':             (1005,  14),
    'homecare_admissions_by_acpr.csv':      (454,   27),
    'home_care_users_by_acpr.csv':          (432,   26),
    'residential_admissions_by_acpr.csv':   (350,   25),
    'residential_users_by_acpr.csv':        (420,   24),
    'service_funding_by_facility.csv':      (37733,  8),
    'abs_population_by_sa3.csv':            (2016,   6),
}

all_passed = True
for fname, exp_shape in expected.items():
    path = os.path.join(CLEAN, fname)
    if os.path.exists(path):
        df = pd.read_csv(path)
        match = df.shape == exp_shape
        status = '✅' if match else '⚠️  shape mismatch'
        print(f'  {status}  {fname}: {df.shape}  (expected {exp_shape})')
        if not match: all_passed = False
    else:
        print(f'  ❌  {fname}: NOT FOUND')
        all_passed = False

print()
if all_passed:
    print('All 9 CSVs generated correctly. Ready for EDA.')
else:
    print('Some files missing or shape mismatch. Check errors above.')
