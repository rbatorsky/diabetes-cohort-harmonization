import os
import glob
import pandas as pd
from harmonization_scripts.config import load_config
from harmonization_scripts.load.loader_health import load_health_spanish_data
from harmonization_scripts.load.loader_ffq import load_ffq_spanish_data

# Preliminary checks
CLEANUP_OLD_QC_TABLES = True
DIFF_REL_HARD = 0.50     # hard flag if HMZ mean differs from RAW by ≥50%
MISS_GAP_PCT_PT = 10.0   # flag missingness gap if ≥10 percentage points




# -----------------------------
# Helpers 
# -----------------------------
def _path_exists(p: str) -> bool:
    try:
        return os.path.exists(p)
    except Exception:
        return False


def _read_csv_safe(path: str) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def _normalize_studyid_inplace(df: pd.DataFrame) -> None:
    for cand in ["studyid", "record_id", "id", "STUDYID", "Record_ID", "redcapid"]:
        if cand in df.columns:
            if cand != "studyid":
                df.rename(columns={cand: "studyid"}, inplace=True)
            return


def _canonicalize_id(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.str.replace(r"\.0+$", "", regex=True)  # drop trailing .0 artifacts
    return s


def _normalize_visit_value(series: pd.Series) -> pd.Series:
    """
    Normalize visit-like values to {'v1','v2','v3','v4'}.
    Handles many REDCap/event variants across PROSPECT + BPRHS.
    """
    s = series.astype(str).str.strip().str.lower()
    s = s.str.replace(r"\s+", " ", regex=True)

    mapping = {
        # plain
        "1": "v1", "2": "v2", "3": "v3", "4": "v4",
        "v1": "v1", "v2": "v2", "v3": "v3", "v4": "v4",
        # common words
        "baseline": "v1", "baseline visit": "v1",
        # REDCap events 
        "baseline_arm_1": "v1",
        "visit 1": "v1", "visit_1": "v1", "visit1": "v1", "visit_1_arm_1": "v1",
        "visit 2": "v2", "visit_2": "v2", "visit2": "v2", "visit_2_arm_1": "v2",
        "visit 3": "v3", "visit_3": "v3", "visit3": "v3", "visit_3_arm_1": "v3",
        "visit 4": "v4", "visit_4": "v4", "visit4": "v4", "visit_4_arm_1": "v4",
        # other event labels
        "event_1_arm_1": "v1",
        # year-style
        "2year_arm_1": "v2", "5year_arm_1": "v3", "8year_arm_1": "v4",
    }
    out = s.map(mapping)

 
    mask = out.isna()
    if mask.any():
        ss = s[mask]
        out.loc[mask & ss.str.contains("baseline")] = "v1"
        for k, v in [("1", "v1"), ("2", "v2"), ("3", "v3"), ("4", "v4")]:
            out.loc[mask & ss.str.contains(fr"visit[_ ]?{k}")] = v
            out.loc[mask & ss.str.contains(fr"{k}\s*year")] = v
            out.loc[mask & ss.str.contains(fr"event[_ ]?{k}.*arm")] = v
        tmp = ss.str.extract(r"(?:visit|event)[_ ]?([1-4]).*arm", expand=True)
        mapv = {"1": "v1", "2": "v2", "3": "v3", "4": "v4"}
        out.loc[mask] = out.loc[mask].fillna(tmp[0].map(mapv))
    return out


def _ensure_visit_column_inplace(df: pd.DataFrame) -> None:
    """Create/standardize 'visit' to {'v1','v2','v3','v4'} if possible."""
    if "visit" in df.columns:
        df["visit"] = _normalize_visit_value(df["visit"])
        return
    if "redcap_event_name" in df.columns:
        df["visit"] = _normalize_visit_value(df["redcap_event_name"])
        return
    for alt in ["hmz_visit_prospect", "vnum", "wave", "event"]:
        if alt in df.columns:
            df["visit"] = _normalize_visit_value(df[alt])
            return


def _concat_safe(a: pd.DataFrame | None, b: pd.DataFrame | None) -> pd.DataFrame | None:
    if a is None and b is None:
        return None
    if a is None:
        return b
    if b is None:
        return a
    return pd.concat([a, b], ignore_index=True, sort=False)


def _augment_raw_pools_with_english(raw_health_all: dict, raw_ffq_all: dict) -> None:
    """
    Keep Spanish loaders as-is. If English files exist, read here and
    append to key 'prospect' used by the validator.
    """
    # ---- PROSPECT Health/SDOH (English) ----
    english_health_paths = [
        load_config()["health_prospect_english"]
    ]
    eng_health_df = None
    for p in english_health_paths:
        if _path_exists(p):
            df = _read_csv_safe(p)
            _normalize_studyid_inplace(df)
            _ensure_visit_column_inplace(df)
            df["cohort"] = "PROSPECT"
            df["language"] = "english"
            eng_health_df = _concat_safe(eng_health_df, df)

    if eng_health_df is not None:
        if "prospect" in raw_health_all:
            raw_health_all["prospect"] = _concat_safe(raw_health_all["prospect"], eng_health_df)
        else:
            raw_health_all["prospect"] = eng_health_df

    # ---- PROSPECT FFQ (English) ----
    english_ffq_paths = [
        load_config()["ffq_prospect_english"]
    ]
    eng_ffq_df = None
    for p in english_ffq_paths:
        if _path_exists(p):
            df = _read_csv_safe(p)
            _normalize_studyid_inplace(df)
            _ensure_visit_column_inplace(df)
            df["cohort"] = "PROSPECT"
            df["language"] = "english"
            eng_ffq_df = _concat_safe(eng_ffq_df, df)

    if eng_ffq_df is not None:
        if "prospect" in raw_ffq_all:
            raw_ffq_all["prospect"] = _concat_safe(raw_ffq_all["prospect"], eng_ffq_df)
        else:
            raw_ffq_all["prospect"] = eng_ffq_df


# utilities for alignment ------------------------------------------------
def _first_valid(x: pd.Series):
    x = x.dropna()
    return x.iloc[0] if not x.empty else pd.NA


def _pick_first_present(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _prepare_table(df: pd.DataFrame, var: str,
                   id_candidates: list[str],
                   ensure_visit: bool = True) -> pd.DataFrame:
    """
    Build a compact table with columns: id, visit, var
    - chooses first present id column, canonicalizes it
    - ensures/normalizes 'visit'
    - collapses repeats to one row per (id, visit) using first non-null var
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["id", "visit", var])

    df = df.copy()

    if ensure_visit:
        _ensure_visit_column_inplace(df)

    id_col = _pick_first_present(df, id_candidates)
    if id_col is None:
        _normalize_studyid_inplace(df)
        id_col = _pick_first_present(df, ["studyid"])
    if id_col is None:
        return pd.DataFrame(columns=["id", "visit", var])

    df["id"] = _canonicalize_id(df[id_col])
    if "visit" in df.columns:
        df["visit"] = _normalize_visit_value(df["visit"])
    else:
        df["visit"] = pd.NA

    keep_cols = ["id", "visit"]
    if var in df.columns:
        keep_cols.append(var)
    else:
        return pd.DataFrame(columns=["id", "visit", var])

    slim = df[keep_cols]

    agg = (
        slim.groupby(["id", "visit"], dropna=False, as_index=False)
            .agg({var: _first_valid})
    )
    return agg


# -----------------------------
# Dimensions & duplicates
# -----------------------------
def _qc_dimensions_and_duplicates_text():
    base = "data"
    inter_dir = os.path.join(base, "intermediate")
    out_dir = os.path.join(base, "output")
    os.makedirs(out_dir, exist_ok=True)

    cfg = load_config()

    output_name = cfg.get(
    "merged_output_filename",
    "df_hmz_bprhs_prospect_2026.csv")

    merged_path = os.path.join(out_dir, output_name)



    if not os.path.exists(merged_path):
        return [f"[ERROR] Final merged file not found: {merged_path}"]

    df_hmz = pd.read_csv(merged_path)

    def load_many(pattern):
        paths = sorted(glob.glob(os.path.join(inter_dir, pattern)))
        return [pd.read_csv(p) for p in paths]

    df_sdoh = load_many("df_hmz_sdoh_*.csv")
    df_health = load_many("df_hmz_health_*.csv")
    df_ffq = load_many("df_hmz_ffq_*.csv")

    total_sdoh_rows = sum(df.shape[0] for df in df_sdoh)
    total_health_rows = sum(df.shape[0] for df in df_health)
    total_ffq_rows = sum(df.shape[0] for df in df_ffq)
    unique_merged_keys = df_hmz[['studyid', 'cohort', 'visit']].drop_duplicates().shape[0]

    sdoh_cols = set().union(*(df.columns for df in df_sdoh)) if df_sdoh else set()
    health_cols = set().union(*(df.columns for df in df_health)) if df_health else set()
    ffq_cols = set().union(*(df.columns for df in df_ffq)) if df_ffq else set()
    merged_cols = set(df_hmz.columns)


    cohorts_visits = {
        'BPRHS': ['v1', 'v2', 'v3', 'v4'],
        'PROSPECT': ['v1', 'v2'],
    }

    # Extra quick checks
    null_studyid = int(df_hmz['studyid'].isna().sum()) if 'studyid' in df_hmz.columns else -1
    null_cohort  = int(df_hmz['cohort'].isna().sum())  if 'cohort'  in df_hmz.columns else -1
    null_visit   = int(df_hmz['visit'].isna().sum())   if 'visit'   in df_hmz.columns else -1
    counts_cv = (
        df_hmz.groupby(['cohort','visit'], dropna=False)
              .size()
              .reset_index(name='n')
              .sort_values(['cohort','visit'])
              .values.tolist()
    )

    def collect_keys(frames):
        if not frames:
            return pd.DataFrame(columns=['studyid','cohort','visit'])
        keep = []
        for d in frames:
            cols = [c for c in ['studyid','cohort','visit'] if c in d.columns]
            if len(cols) == 3:
                keep.append(d[cols].dropna().drop_duplicates())
        return pd.concat(keep, ignore_index=True) if keep else pd.DataFrame(columns=['studyid','cohort','visit'])



    # Schema sanity
    hi_miss = []
    if df_hmz.shape[0] > 0:
        for col in df_hmz.columns:
            if col in {'studyid','cohort','visit'}:
                continue
            frac = float(df_hmz[col].isna().mean())
            if frac >= 0.95:
                hi_miss.append((col, round(frac, 3)))
    suspicious = [c for c in df_hmz.columns if c.startswith('Unnamed:')]

    allowed_cohort = {'BPRHS','PROSPECT'}
    allowed_visit  = {'v1','v2','v3','v4'}
    bad_cohort = sorted(set(df_hmz['cohort'].dropna()) - allowed_cohort) if 'cohort' in df_hmz.columns else []
    bad_visit  = sorted(set(df_hmz['visit'].dropna())  - allowed_visit)  if 'visit'  in df_hmz.columns else []

    lines = []
    w = lines.append

    w("Quality Control Report — Dimensions & Duplicates")
    w(f"Final merged dataset: {os.path.join('data','output', output_name)}")
    w(f"Final merged shape: {df_hmz.shape}")
    w("")
    w("Row counts (inputs):")
    w(f"  SDOH total rows:    {total_sdoh_rows}")
    w(f"  Health total rows:  {total_health_rows}")
    w(f"  FFQ total rows:     {total_ffq_rows}")
    w(f"  Sum of inputs:      {total_sdoh_rows + total_health_rows + total_ffq_rows}")
    w(f"Unique (studyid, cohort, visit) in merged: {unique_merged_keys}")
    w("")
    if df_hmz.shape[0] >= unique_merged_keys:
        w("Row check: OK (merged row count is consistent with unique id combinations).")
    else:
        w("Row check: WARNING (merged row count < unique id combinations).")
    
    w("")
    w("Column counts:")
    w(f"  SDOH columns:    {len(sdoh_cols)}")
    w(f"  Health columns:  {len(health_cols)}")
    w(f"  FFQ columns:     {len(ffq_cols)}")
    w(f"  Merged columns:  {len(merged_cols)}")
    
    w("")
    w("Key integrity:")
    w(f"  Null studyid: {null_studyid}")
    w(f"  Null cohort:  {null_cohort}")
    w(f"  Null visit:   {null_visit}")
    
    w("  Counts by (cohort, visit):")
    for c, v, n in counts_cv:
        w(f"    {c} {v}: {n}")


    w("")
    w("Schema sanity:")
    if hi_miss:
        w(f"  Columns ≥95% missing: {len(hi_miss)} (showing up to 10)")
        for col, frac in hi_miss[:10]:
            w(f"    {col}: {frac}")
    else:
        w("  No columns ≥95% missing (excluding keys).")
    if suspicious:
        w(f"  Suspicious column names (e.g., from CSV index): {suspicious}")
    else:
        w("  No suspicious column names detected.")

    w("")
    w("Allowed category validation:")
    w(f"  Unexpected cohort values: {bad_cohort if bad_cohort else 'none'}")
    w(f"  Unexpected visit values:  {bad_visit  if bad_visit  else 'none'}")

    w("")
    w("Duplicate studyid checks by cohort/visit:")
    for cohort, visits in cohorts_visits.items():
        for visit in visits:
            subset = df_hmz[(df_hmz['cohort'] == cohort) & (df_hmz['visit'] == visit)]
            dups = subset[subset['studyid'].duplicated(keep=False)]
            if dups.empty:
                w(f"  {cohort} {visit}: no duplicates.")
            else:
                ids = dups['studyid'].drop_duplicates().head(10).tolist()
                w(f"  {cohort} {visit}: {dups.shape[0]} duplicate rows (by studyid). Example ids: {ids}")
    w("")
    dup_keys = df_hmz[df_hmz.duplicated(subset=['studyid', 'cohort', 'visit'], keep=False)]
    if dup_keys.empty:
        w("Duplicate key check (studyid, cohort, visit): none.")
    else:
        n_dup = int(dup_keys.shape[0])
        examples = (
            dup_keys[['studyid', 'cohort', 'visit']]
            .drop_duplicates()
            .head(10)
            .to_dict(orient='records')
        )
        w(f"Duplicate key check: {n_dup} duplicated rows. Examples: {examples}")

    return lines


# -----------------------------
# Variable checks
# -----------------------------
def _run_variable_checks(harmonized_data: pd.DataFrame, cfg) -> pd.DataFrame:
    checks_sdoh = [
        ("BPRHS",    "v1", "bprhs_0",  "age",       "hmz_sdoh_age"),
        ("BPRHS",    "v2", "bprhs_2",  "age",       "hmz_sdoh_age"),
        ("PROSPECT", "v1", "prospect", "age_calc",  "hmz_sdoh_age"),
    ]
    checks_health = [
        ("BPRHS",    "v1", "bprhs_0",  "glyhgb",      "hmz_health_lab_a1c"),
        ("BPRHS",    "v2", "bprhs_2",  "glyhgb_2yr",  "hmz_health_lab_a1c"),
        ("PROSPECT", "v1", "prospect", "lab6",        "hmz_health_lab_a1c"),
        ("BPRHS",    "v1", "bprhs_0",  "bmi",      "hmz_health_ant_bmi"),
        ("BPRHS",    "v2", "bprhs_2",  "bmi_2yr",  "hmz_health_ant_bmi"),
        ("PROSPECT", "v1", "prospect", "bmi",        "hmz_health_ant_bmi"),
        ("BPRHS",    "v1", "bprhs_0",  "hip",      "hmz_health_ant_hip"),
        ("BPRHS",    "v2", "bprhs_2",  "hip_2yr",  "hmz_health_ant_hip"),
        ("PROSPECT", "v1", "prospect", "hc_avg",   "hmz_health_ant_hip"),
        ("BPRHS",    "v1", "bprhs_0",  "chol",      "hmz_health_lab_chol"),
        ("BPRHS",    "v2", "bprhs_2",  "chol_2yr",  "hmz_health_lab_chol"),
        ("PROSPECT", "v1", "prospect", "lab1",   "hmz_health_lab_chol"),
        ("BPRHS",    "v1", "bprhs_0",  "ldl",      "hmz_health_lab_ldl"),
        ("BPRHS",    "v2", "bprhs_2",  "ldl_2yr",  "hmz_health_lab_ldl"),
        ("PROSPECT", "v1", "prospect", "lab2",      "hmz_health_lab_ldl"),
    ]
    checks_ffq = [
        ("BPRHS",    "v1", "bprhs_0",  "supdur_1",    "hmz_ffq_sup_dur_1"),
        ("PROSPECT", "v1", "prospect", "supdur1",    "hmz_ffq_sup_dur_1"),]

    # Load Spanish raw
    raw_health_all = load_health_spanish_data(cfg)
    raw_ffq_all = load_ffq_spanish_data(cfg)
    # Optionally augment with English raw (if present on disk)
    _augment_raw_pools_with_english(raw_health_all, raw_ffq_all)

    var_results = []

    # id per cohort/source
    HMZ_ID_CANDS_BPRHS     = ["studyid"]
    HMZ_ID_CANDS_PROSPECT  = ["studyid", "hmz_record_id_prospect", "hmz_record_id_prospect_v1", "hmz_record_id_prospect_v2"]
    RAW_ID_CANDS_COMMON    = ["studyid", "record_id", "redcapid"]

    def run_checks(checks, domain, raw_pool):
        nonlocal var_results
        print(f"\n[DEBUG] Running checks for domain={domain} with raw keys: {list(raw_pool.keys()) if isinstance(raw_pool, dict) else 'n/a'}")

        for cohort, visit, raw_key, raw_var, hmz_var in checks:
            print(f"\n=== {domain} | {cohort} {visit} | HMZ={hmz_var} vs RAW={raw_var} (key={raw_key}) ===")

            # Slice HMZ for cohort+visit;
            hmz_slice = harmonized_data.loc[
                (harmonized_data["cohort"] == cohort) & (harmonized_data["visit"] == visit)
            ]
            if hmz_slice.empty:
                print("[Skip] HMZ slice is empty.")
                continue
            if hmz_var not in hmz_slice.columns:
                print(f"[Skip] HMZ column not found: {hmz_var}")
                continue

            raw_df = raw_pool.get(raw_key) if isinstance(raw_pool, dict) else None
            if raw_df is None or raw_df.empty:
                print(f"[Skip] RAW key not available or empty: {raw_key}")
                continue
            if raw_var not in raw_df.columns:
                print(f"[Skip] RAW column not found: {raw_var}")
                continue

            # Build compact tables with unified id/visit + collapse repeats
            hmz_ids = HMZ_ID_CANDS_BPRHS if cohort == "BPRHS" else HMZ_ID_CANDS_PROSPECT
            raw_ids = RAW_ID_CANDS_COMMON

            hmz_tbl = _prepare_table(hmz_slice, hmz_var, hmz_ids, ensure_visit=True)
            raw_tbl = _prepare_table(raw_df,  raw_var, raw_ids, ensure_visit=True)

            print(f"[DEBUG] HMZ rows={hmz_tbl.shape[0]} (unique id/visit), RAW rows={raw_tbl.shape[0]} after collapse")
            print(f"[DEBUG] HMZ id sample:\n{hmz_tbl.head(3)}")
            print(f"[DEBUG] RAW id sample:\n{raw_tbl.head(3)}")

            # 1) join on (id, visit)
            aligned = hmz_tbl.merge(raw_tbl, on=["id", "visit"], how="inner", suffixes=("_hmz", "_raw"))
            print(f"[DEBUG] Aligned on (id, visit): {aligned.shape[0]} pairs")

            # if too few matches, fall back to id-only
            min_target = max(10, int(0.05 * min(hmz_tbl.shape[0], raw_tbl.shape[0])))
            if aligned.shape[0] < min_target:
                print(f"[DEBUG] Few matches (<{min_target}) on (id, visit). Falling back to id-only alignment.")
                hmz_tbl_id = hmz_tbl.groupby("id", as_index=False).agg({hmz_var: _first_valid})
                raw_tbl_id = raw_tbl.groupby("id", as_index=False).agg({raw_var: _first_valid})
                aligned = hmz_tbl_id.merge(raw_tbl_id, on="id", how="inner", suffixes=("_hmz", "_raw"))
                print(f"[DEBUG] Aligned on id-only: {aligned.shape[0]} pairs")

            if aligned.empty:
                print("[Skip] Alignment produced 0 pairs.")
                continue

            # pull columns
            hmz_raw = aligned[hmz_var]
            raw_raw = aligned[raw_var]

            # coerce to numeric (strings like " " -> NaN)
            hmz_num = pd.to_numeric(hmz_raw, errors="coerce")
            raw_num = pd.to_numeric(raw_raw, errors="coerce")

            # counts of values that became NaN due to non-numeric content
            hmz_nonnum = int(hmz_raw.notna().sum() - hmz_num.notna().sum())
            raw_nonnum = int(raw_raw.notna().sum() - raw_num.notna().sum())

            # use numeric versions going forward
            hmz = hmz_num
            raw = raw_num

            print("\n[HMZ] describe():")
            print(hmz.describe())
            print("[HMZ] missing (after numeric coercion):", hmz.isna().sum(), "| non-numeric:", hmz_nonnum)

            print("\n[RAW] describe():")
            print(raw.describe())
            print("[RAW] missing (after numeric coercion):", raw.isna().sum(), "| non-numeric:", raw_nonnum)

            preview = pd.DataFrame({"hmz": hmz.reset_index(drop=True),
                                    "raw": raw.reset_index(drop=True)})
            print("\n[Sample comparison]")
            print(preview.head(10))

            hmz_mean = float(hmz.mean(skipna=True)) if hmz.notna().any() else None
            raw_mean = float(raw.mean(skipna=True)) if raw.notna().any() else None
            hmz_std  = float(hmz.std(skipna=True))  if hmz.notna().any() else None
            raw_std  = float(raw.std(skipna=True))  if raw.notna().any() else None

            var_results.append({
                "domain": domain, "cohort": cohort, "visit": visit,
                "hmz_var": hmz_var, "raw_var": raw_var,
                "hmz_missing": int(hmz.isna().sum()),
                "raw_missing": int(raw.isna().sum()),
                "hmz_non_numeric": hmz_nonnum,
                "raw_non_numeric": raw_nonnum,
                "hmz_mean": hmz_mean, "raw_mean": raw_mean,
                "hmz_std": hmz_std, "raw_std": raw_std,
                "n_hmz": int(hmz.shape[0]), "n_raw": int(raw.shape[0]),
            })

    run_checks(checks_sdoh,   "SDOH",   raw_health_all)
    run_checks(checks_health, "HEALTH", raw_health_all)
    run_checks(checks_ffq,    "FFQ",    raw_ffq_all)

    if var_results:
        return pd.DataFrame(var_results)
    return pd.DataFrame(columns=[
        "domain","cohort","visit","hmz_var","raw_var",
        "hmz_missing","raw_missing","hmz_non_numeric","raw_non_numeric",
        "hmz_mean","raw_mean","hmz_std","raw_std","n_hmz","n_raw"
    ])


# -----------------------------
#  TEXT report
# -----------------------------
def _write_unified_qc_text(dim_lines, var_df, output_dir, harmonized_data=None):
    path = os.path.join(output_dir, "qc_report.txt")

    desired_cols = [
"domain", "cohort", "visit", 
    "hmz_var", "raw_var",
    "n_hmz", "n_raw",
    "hmz_missing", "raw_missing",
    "hmz_non_numeric", "raw_non_numeric",
    "hmz_mean", "raw_mean",
    "hmz_std", "raw_std"
    ]
    
    cols = [c for c in desired_cols if (not var_df.empty and c in var_df.columns)] or desired_cols

    def fmt_val(v):
        if pd.isna(v):
            return ""
        if isinstance(v, float):
            s = f"{v:.6f}".rstrip("0").rstrip(".")
            return s if s else "0"
        return str(v)

    # compute column widths from data
    col_widths = {c: max(10, len(c)) for c in cols}
    if not var_df.empty:
        for c in cols:
            mx = var_df[c].map(fmt_val).map(len).max()
            col_widths[c] = min(max(col_widths[c], int(mx)), 32)

    def row_to_line(row_dict):
        return "  ".join(fmt_val(row_dict.get(c, "")).ljust(col_widths[c]) for c in cols)

    header_line = "  ".join(c.ljust(col_widths[c]) for c in cols)
    sep_line    = "  ".join("-" * col_widths[c] for c in cols)
    
  
    
  
# -----------------------------
# Cross-cohort HMZ vs HMZ checks (BPRHS vs PROSPECT)
# -----------------------------   


    cross_checks = {
        "SDOH":  [("v1", "hmz_sdoh_age")],
        "HEALTH":[("v1", "hmz_health_lab_a1c"),
                  ("v1", "hmz_health_ant_bmi"),
                  ("v1", "hmz_health_ant_hip"),
                  ("v1", "hmz_health_lab_chol"),
                  ("v1", "hmz_health_lab_ldl")],
        "FFQ":   [("v1", "hmz_ffq_sup_dur_1")],
    }

    def _coerce_numeric_local(s: pd.Series):
        s_num = pd.to_numeric(s, errors="coerce")
        nonnum = int(s.notna().sum() - s_num.notna().sum())
        return s_num, nonnum

    def _smd_local(mean_a, sd_a, n_a, mean_b, sd_b, n_b):
        # Cohen/Hedges SMD with pooled SD
        if None in (mean_a, sd_a, mean_b, sd_b) or n_a is None or n_b is None:
            return None
        if n_a <= 1 or n_b <= 1 or sd_a in (None, 0) or sd_b in (None, 0):
            return None
        pooled_var = ((n_a - 1) * (sd_a ** 2) + (n_b - 1) * (sd_b ** 2)) / (n_a + n_b - 2)
        if pooled_var <= 0:
            return None
        return (mean_a - mean_b) / (pooled_var ** 0.5)

    cross_rows = []
    if isinstance(harmonized_data, pd.DataFrame) and not harmonized_data.empty:
        for domain, items in cross_checks.items():
            for visit, hmz_var in items:
                b_slice = harmonized_data[(harmonized_data["cohort"] == "BPRHS") &
                                          (harmonized_data["visit"] == visit)]
                p_slice = harmonized_data[(harmonized_data["cohort"] == "PROSPECT") &
                                          (harmonized_data["visit"] == visit)]
                if b_slice.empty or p_slice.empty:
                    continue
                if hmz_var not in b_slice.columns or hmz_var not in p_slice.columns:
                    continue

              
                try:
                    b_tbl = _prepare_table(b_slice, hmz_var, ["studyid"], ensure_visit=True)
                    p_tbl = _prepare_table(p_slice, hmz_var,
                                           ["studyid","hmz_record_id_prospect",
                                            "hmz_record_id_prospect_v1","hmz_record_id_prospect_v2"],
                                           ensure_visit=True)
                    b_vals = b_tbl[hmz_var]; p_vals = p_tbl[hmz_var]
                except NameError:
                    b_vals = b_slice[hmz_var]; p_vals = p_slice[hmz_var]

                b_num, b_nonnum = _coerce_numeric_local(b_vals)
                p_num, p_nonnum = _coerce_numeric_local(p_vals)

                b_n = int(b_num.notna().sum()); p_n = int(p_num.notna().sum())
                b_miss = int(b_num.isna().sum()); p_miss = int(p_num.isna().sum())
                b_mean = float(b_num.mean(skipna=True)) if b_n else None
                p_mean = float(p_num.mean(skipna=True)) if p_n else None
                b_std  = float(b_num.std(skipna=True))  if b_n > 1 else None
                p_std  = float(p_num.std(skipna=True))  if p_n > 1 else None
                smd    = _smd_local(b_mean, b_std, b_n, p_mean, p_std, p_n)

                cross_rows.append({
                    "domain": domain, "visit": visit, "hmz_var": hmz_var,
                    "bprhs_n": b_n, "prospect_n": p_n,
                    "bprhs_missing": b_miss, "prospect_missing": p_miss,
                    "bprhs_non_numeric": b_nonnum, "prospect_non_numeric": p_nonnum,
                    "bprhs_mean": b_mean, "prospect_mean": p_mean,
                    "bprhs_std": b_std, "prospect_std": p_std,
                    "smd": smd
                })

    cross_df = pd.DataFrame(cross_rows, columns=[
        "domain","visit","hmz_var",
        "bprhs_n","prospect_n",
        "bprhs_missing","prospect_missing",
        "bprhs_non_numeric","prospect_non_numeric",
        "bprhs_mean","prospect_mean",
        "bprhs_std","prospect_std",
        "smd"
    ])

    # Cross-cohort section 
    cross_cols = [
        "domain","visit","hmz_var",
        "bprhs_n","prospect_n",
        "bprhs_missing","prospect_missing",
        "bprhs_non_numeric","prospect_non_numeric",
        "bprhs_mean","prospect_mean",
        "bprhs_std","prospect_std",
        "smd"
    ]
    cwidths = {c: max(10, len(c)) for c in cross_cols}
    if not cross_df.empty:
        for c in cross_cols:
            mx = cross_df[c].map(fmt_val).map(len).max()
            cwidths[c] = min(max(cwidths[c], int(mx)), 32)

    def cross_row_to_line(row_dict):
        return "  ".join(fmt_val(row_dict.get(c, "")).ljust(cwidths[c]) for c in cross_cols)

    cross_header = "  ".join(c.ljust(cwidths[c]) for c in cross_cols)
    cross_sep    = "  ".join("-" * cwidths[c] for c in cross_cols)


    # ---------- Additional Checks (compact) -----------
    extra_lines = []
    x = extra_lines.append

    # --- STRUCTURAL CHECKS (placed FIRST) ---
    if isinstance(harmonized_data, pd.DataFrame) and not harmonized_data.empty:
        df = harmonized_data

        x("Structural — Expected variable presence:")
        expected_vars = ["hmz_sdoh_age", "hmz_health_lab_a1c", "hmz_ffq_sup_dur_1"]
        missing_expected = [v for v in expected_vars if v not in df.columns]
        x(f"  Missing expected hmz_ variables: {missing_expected if missing_expected else 'none'}")

        # Dtype summary
        n_num = df.select_dtypes(include=['number']).shape[1]
        n_non = df.shape[1] - n_num
        x("Structural — Dtype summary:")
        x(f"  Numeric columns: {n_num} | Non-numeric columns: {n_non}")

        # Top missingness
        miss = df.isna().mean().sort_values(ascending=False)
        top10 = miss.head(10)
        if top10.shape[0] > 0:
            x("Structural — Top 10 missingness (fraction):")
            for k, v in top10.items():
                x(f"  {k}: {round(float(v),3)}")

        # Plausibility ranges
        def _count_outside(series, low=None, high=None, nonneg=False):
            s = series.dropna()
            if nonneg:
                return int((s < 0).sum())
            cnt = 0
            if low is not None:
                cnt += int((s < low).sum())
            if high is not None:
                cnt += int((s > high).sum())
            return cnt

        if "hmz_sdoh_age" in df.columns:
            bad = _count_outside(df["hmz_sdoh_age"], low=0, high=120)
            x(f"Content — Age plausibility (0–120): {bad} out-of-range values.")
        if "hmz_health_lab_a1c" in df.columns:
            bad = _count_outside(df["hmz_health_lab_a1c"], low=3, high=20)
            x(f"Content — A1c plausibility (3–20): {bad} out-of-range values.")
        if "hmz_ffq_sup_dur_1" in df.columns:
            bad = _count_outside(df["hmz_ffq_sup_dur_1"], nonneg=True)
            x(f"Content — Supplement duration nonnegative: {bad} negatives.")

    # --- HMZ vs RAW FLAGS  ---
 
# list of variables that were not transformed
    NO_XFORM_HMZ = {
    "hmz_health_ant_bp_sys", "hmz_health_ant_bp_dias", "hmz_health_ant_bmi",
    "hmz_health_lab_chol", "hmz_health_lab_ldl", "hmz_health_lab_hdl",
    "hmz_health_lab_trig", "hmz_health_lab_gluc", "hmz_health_lab_a1c",
    "hmz_health_lab_bun", "hmz_health_lab_creat", "hmz_health_lab_alb",
    "hmz_health_lab_insulin", "hmz_health_lab_platelet",
    "hmz_health_ant_pounds_i", "hmz_health_hb_alc4a", "hmz_health_hb_slp2",
    "hmz_sdoh_sex", "hmz_sdoh_hc", "hmz_sdoh_hc_0_5", "hmz_sdoh_hc_6_12",
    "hmz_sdoh_soc1", "hmz_ffq_sup_use", "hmz_ffq_gramamt", "hmz_ffq_kcal",
    "hmz_ffq_kj", "hmz_ffq_tcho", "hmz_ffq_fat", "hmz_ffq_pro",
    "hmz_ffq_vpro", "hmz_ffq_apro", "hmz_ffq_alc", "hmz_ffq_chol",
    "hmz_ffq_sfa", "hmz_ffq_mfa", "hmz_ffq_pfa", "hmz_ffq_fruc",
    "hmz_ffq_gala", "hmz_ffq_gluc", "hmz_ffq_lact", "hmz_ffq_malt",
    "hmz_ffq_sucr", "hmz_ffq_star", "hmz_ffq_tsugar", "hmz_ffq_dfib",
    "hmz_ffq_wsdf", "hmz_ffq_ifib", "hmz_ffq_pect", "hmz_ffq_va",
    "hmz_ffq_acar", "hmz_ffq_bceq", "hmz_ffq_bcar", "hmz_ffq_rl",
    "hmz_ffq_varae", "hmz_ffq_vare", "hmz_ffq_bcry", "hmz_ffq_lyco",
    "hmz_ffq_lz", "hmz_ffq_vb6", "hmz_ffq_vb12", "hmz_ffq_fol",
    "hmz_ffq_dfe", "hmz_ffq_nfol", "hmz_ffq_sfol", "hmz_ffq_nia",
    "hmz_ffq_niaeq", "hmz_ffq_pant", "hmz_ffq_thi", "hmz_ffq_rib",
    "hmz_ffq_choline", "hmz_ffq_ttc", "hmz_ffq_atc", "hmz_ffq_natatoc",
    "hmz_ffq_synatoc", "hmz_ffq_btc", "hmz_ffq_dtc", "hmz_ffq_gtc",
    "hmz_ffq_vc", "hmz_ffq_vd", "hmz_ffq_vite", "hmz_ffq_vk", "hmz_ffq_ca",
    "hmz_ffq_cu", "hmz_ffq_fe", "hmz_ffq_k", "hmz_ffq_na", "hmz_ffq_mg",
    "hmz_ffq_mn", "hmz_ffq_se", "hmz_ffq_zn", "hmz_ffq_p",
    "hmz_ffq_s04_0", "hmz_ffq_s06_0", "hmz_ffq_s08_0", "hmz_ffq_s10_0",
    "hmz_ffq_s12_0", "hmz_ffq_s14_0", "hmz_ffq_s16_0", "hmz_ffq_s17_0",
    "hmz_ffq_s18_0", "hmz_ffq_s20_0", "hmz_ffq_s22_0",
    "hmz_ffq_m14_1", "hmz_ffq_m16_1", "hmz_ffq_m18_1", "hmz_ffq_m20_1",
    "hmz_ffq_m22_1",
    "hmz_ffq_p18_2", "hmz_ffq_p18_3", "hmz_ffq_p18_4", "hmz_ffq_p20_4",
    "hmz_ffq_p20_5", "hmz_ffq_p22_5", "hmz_ffq_p22_6",
    "hmz_ffq_f161t", "hmz_ffq_f181t", "hmz_ffq_f182t", "hmz_ffq_ttfa",
    "hmz_ffq_omega3", "hmz_ffq_cyst", "hmz_ffq_glut", "hmz_ffq_glyc",
    "hmz_ffq_isol", "hmz_ffq_hist", "hmz_ffq_leuc", "hmz_ffq_lysi",
    "hmz_ffq_meth", "hmz_ffq_phen", "hmz_ffq_prol", "hmz_ffq_seri",
    "hmz_ffq_thre", "hmz_ffq_tryp", "hmz_ffq_alan", "hmz_ffq_argi",
    "hmz_ffq_aspa", "hmz_ffq_tyro", "hmz_ffq_vali", "hmz_ffq_mh3",
    "hmz_ffq_aspt", "hmz_ffq_glyt", "hmz_ffq_coum", "hmz_ffq_daid",
    "hmz_ffq_betaine", "hmz_ffq_bioa", "hmz_ffq_formon", "hmz_ffq_geni",
    "hmz_ffq_eryth", "hmz_ffq_mani", "hmz_ffq_inos", "hmz_ffq_lactl",
    "hmz_ffq_pini", "hmz_ffq_sorb", "hmz_ffq_xyli", "hmz_ffq_acho",
    "hmz_ffq_asugar", "hmz_ffq_sucl", "hmz_ffq_acesk", "hmz_ffq_oxal",
    "hmz_ffq_phyt", "hmz_ffq_sp", "hmz_ffq_caf", "hmz_ffq_ash",
    "hmz_ffq_w", "hmz_ffq_nitrogen"}
    
 
    if isinstance(var_df, pd.DataFrame) and not var_df.empty:
        x("Cross-dataset — HMZ vs RAW consistency flags (no-transform variables only):")
    flags = []
    for _, r in var_df.iterrows():
        hmz_name = str(r.get("hmz_var", "")).strip()
        if hmz_name not in NO_XFORM_HMZ:
            continue

        hm = r.get("hmz_mean", None)
        rw = r.get("raw_mean", None)

        # Mean differences (absolute + relative to RAW)
        if pd.notna(hm) and pd.notna(rw):
            hm = float(hm); rw = float(rw)
            diff = abs(hm - rw)
            base = max(abs(rw), 1e-9)  # avoid /0
            rel  = diff / base

            # Hard flag at ≥50% relative difference (tunable)
            if rel >= DIFF_REL_HARD:
                flags.append(
                    f"[FLAG≥{int(DIFF_REL_HARD*100)}%] {r['domain']} {r['cohort']} {r['visit']} "
                    f"{r['hmz_var']} vs {r['raw_var']}: mean diff={diff:.3g} "
                    f"({rel*100:.1f}% of RAW)"
                )

            # Heuristic flag (0.1 abs & 5% rel)
            if (diff > 0.1) and (rel > 0.05):
                flags.append(
                    f"{r['domain']} {r['cohort']} {r['visit']} {r['hmz_var']} vs {r['raw_var']}: "
                    f"mean diff={diff:.3g} (rel={rel*100:.1f}%) — check transformation/scale."
                )

        # Missingness gap (≥ N percentage points)
        hm_miss = r.get("hmz_missing", None)
        rw_miss = r.get("raw_missing", None)
        n_h     = r.get("n_hmz", None)
        n_r     = r.get("n_raw", None)
        if all(pd.notna(v) for v in [hm_miss, rw_miss, n_h, n_r]) and n_h and n_r:
            hm_rate = float(hm_miss) / max(int(n_h), 1)
            rw_rate = float(rw_miss) / max(int(n_r), 1)
            gap_pp  = (hm_rate - rw_rate) * 100.0
            if abs(gap_pp) >= MISS_GAP_PCT_PT:
                flags.append(
                    f"{r['domain']} {r['cohort']} {r['visit']} {r['hmz_var']} vs {r['raw_var']}: "
                    f"missing gap={gap_pp:.1f} pp"
                )

        # Non-numeric coercion counts
        nn_h = int(r.get("hmz_non_numeric", 0) or 0)
        nn_r = int(r.get("raw_non_numeric", 0) or 0)
        if nn_h > 0 or nn_r > 0:
            flags.append(
                f"{r['domain']} {r['cohort']} {r['visit']} {r['hmz_var']} vs {r['raw_var']}: "
                f"non-numeric → HMZ={nn_h}, RAW={nn_r}"
            )

        # N-size mismatch (informational)
        n_h = r.get("n_hmz", None); n_r = r.get("n_raw", None)
        if pd.notna(n_h) and pd.notna(n_r) and int(n_h) != int(n_r):
            flags.append(
                f"{r['domain']} {r['cohort']} {r['visit']} {r['hmz_var']} vs {r['raw_var']}: "
                f"n mismatch HMZ={int(n_h)} RAW={int(n_r)}"
            )

    if flags:
        for line in flags[:30]:
            x("  " + line)
        if len(flags) > 30:
            x(f"  ... and {len(flags)-30} more")
    else:
        x(f"  No material differences flagged among no-transform variables "
          f"(≥{int(DIFF_REL_HARD*100)}% mean gap and {MISS_GAP_PCT_PT:.0f}pp missingness).")


    # -------------- write file --------------
    with open(path, "w", encoding="utf-8") as f:
        # dimensions section
        f.write("QC REPORT — Dimensions & Duplicates\n")
        f.write("=" * 72 + "\n")
        for line in dim_lines:
            f.write(str(line) + "\n")

        # variable checks section (table)
        f.write("\nQC REPORT — Variable Checks\n")
        f.write("=" * 72 + "\n")
        if var_df.empty:
            f.write("(no variable checks)\n")
        else:
            f.write(header_line + "\n")
            f.write(sep_line + "\n")
            for _, row in var_df.iterrows():
                f.write(row_to_line(row.to_dict()) + "\n")

        # Cross-cohort section (HMZ BPRHS vs HMZ PROSPECT)
        f.write("\nQC REPORT — Cross-Cohort HMZ (BPRHS vs PROSPECT)\n")
        f.write("=" * 72 + "\n")
        if cross_df.empty:
            f.write("(no cross-cohort checks)\n")
        else:
            f.write(cross_header + "\n")
            f.write(cross_sep + "\n")
            for _, row in cross_df.iterrows():
                f.write(cross_row_to_line(row.to_dict()) + "\n")

        # additional checks
        if extra_lines:
            f.write("\nQC REPORT — Additional Checks\n")
            f.write("=" * 72 + "\n")
            for line in extra_lines:
                f.write(str(line) + "\n")

    print(f" Unified QC report saved to: {path}")
    return path


def _cleanup_old_qc_artifacts(output_dir: str):
    """Remove legacy CSV/XLSX QC tables so the only artifact left is the txt report."""
    if not CLEANUP_OLD_QC_TABLES:
        return
    leftovers = [
        "qc_variable_checks.csv",
        "qc_variable_checks.xlsx",
        "qc_variables.csv",
        "variable_checks.csv",
        "var_checks.csv",
    ]
    for name in leftovers:
        fp = os.path.join(output_dir, name)
        if os.path.exists(fp):
            try:
                os.remove(fp)
                print(f"[cleanup] removed legacy artifact: {fp}")
            except Exception as e:
                print(f"[cleanup] could not remove {fp}: {e}")


# -----------------------------
# Missingness / availability coding
# -----------------------------
AVAIL_LABELS = {
    0: "answered",
    1: "not administered",
    2: "respondent absent",
    3: "unanswered",
    4: "routed out",
    5: "lost to follow-up",
}

# Gate variables and the follow-up variables skipped according to the gate's answer.
# A value of "prefix:<stem>" expands to every modality variable starting with that stem.
# By default a follow-up is skipped when the gate is answered and is not "yes" (1);
# gates with a different rule are listed in ROUTING_SKIP_RULE.
ROUTING = {
    "hmz_ffq_sup_use": [f"hmz_ffq_sup_dur_{i}" for i in range(1, 19)],
    "hmz_health_med_1": ["hmz_health_med_1_medication", "hmz_health_med_1_today", "hmz_health_med_1_age"],
    "hmz_health_med_bp": ["hmz_health_med_bp_medication", "hmz_health_med_bp_today"],
    "hmz_health_med_overweight": ["hmz_health_med_overweight_medication", "hmz_health_med_overweight_today"],
    "hmz_health_med_angina": ["hmz_health_med_angina_medication", "hmz_health_med_angina_today"],
    "hmz_health_med_heart_attack": ["hmz_health_med_heart_attack_medication", "hmz_health_med_heart_attack_today"],
    "hmz_health_med_heart_failure": ["hmz_health_med_heart_failure_medication", "hmz_health_med_heart_failure_today"],
    "hmz_health_med_heart_disease": ["hmz_health_med_heart_disease_medication", "hmz_health_med_heart_disease_today"],
    "hmz_health_med_stroke": ["hmz_health_med_stroke_medication", "hmz_health_med_stroke_today"],
    "hmz_health_med_kidney_disease": ["hmz_health_med_kidney_disease_medication", "hmz_health_med_kidney_disease_today"],
    "hmz_health_med_hepatitis": ["hmz_health_med_hepatitis_medication", "hmz_health_med_hepatitis_today",
                                 "hmz_health_med_hepatitis_type"],
    "hmz_health_med_arthritis": ["hmz_health_med_arthritis_medication", "hmz_health_med_arthritis_today"],
    "hmz_health_med_osteoporosis": ["hmz_health_med_osteoporosis_medication", "hmz_health_med_osteoporosis_today"],
    "hmz_health_med_eye": ["hmz_health_med_eye_medication", "hmz_health_med_eye_today"],
    "hmz_health_med_anxiety": ["hmz_health_med_anxiety_medication", "hmz_health_med_anxiety_today"],
    "hmz_health_med_depression": ["hmz_health_med_depression_medication", "hmz_health_med_depression_today"],
    "hmz_health_med_cancer": "prefix:hmz_health_med_cancer_",
    "hmz_health_med_respiratory": "prefix:hmz_health_med_respiratory_",
    "hmz_health_med_stomach_intestine": "prefix:hmz_health_med_stomach_intestine_",
    "hmz_health_hb_alcohol": ["hmz_health_hb_alc4a", "hmz_health_hb_alc4b"],
    "hmz_health_hb_tob3": ["hmz_health_hb_tobacco_home", "hmz_health_hb_tobacco_work",
                           "hmz_health_hb_tobacco_car", "hmz_health_hb_tobacco_other"],
    "hmz_sdoh_pdq_2h": ["hmz_sdoh_pdq_2h_other"],
    "hmz_sdoh_pdq_2i": ["hmz_sdoh_pdq_2i_other"],
    "hmz_sdoh_pdq_4i": ["hmz_sdoh_pdq_4i_other"],
    "hmz_sdoh_insurance": ["hmz_sdoh_no_insurance"],
    # hmz_health_hb_slp_snore -> hmz_health_hb_slp_snore_ii removed: not a gate question
}

# Gates whose follow-up is skipped on a rule other than "answered and not 1".
# ("not_equal", v): skipped when answered and != v;  ("equal", v): skipped when == v.
ROUTING_SKIP_RULE = {
    "hmz_sdoh_pdq_2i": ("not_equal", 8),     # "other, specify" asked only when main reason is 8 (other)
    "hmz_sdoh_pdq_4i": ("not_equal", 8),
    "hmz_sdoh_insurance": ("equal", 1),      # time without insurance asked only of people without insurance
}

# Count gates: follow-up <stem>k is skipped when the count is below k.
ROUTING_COUNT = {
    "hmz_sdoh_soc_support_i": "hmz_sdoh_soc_support_ii_",   # relationship of person k, k = 1..10
}


def _qc_missingness(harmonized_data: pd.DataFrame, output_dir: str,
                    avail_filename: str = "qc_missingness.csv"):
    """
    Decompose missingness in the harmonized dataset into its sources and write a
    cell-level availability-coded copy of the dataset.

    A participant has data at a visit if at least one harmonized variable has a
    non-empty, non-zero value for them at that visit.

    Codes: 0 answered; 1 not administered (no participant with data at that cohort
    and visit has a value for the variable); 2 respondent absent (no data at this
    visit, data at an earlier and a later visit); 3 unanswered; 4 routed out
    (would be 3, but a gate question means it was not asked); 5 lost to follow-up
    (no data at this or any later visit, data at an earlier one). Codes 2 and 5
    apply to all cells of the visit, including placeholder 0s. Records are added
    for visits at which a participant has no record, so they can be coded. Visits
    before a participant's first visit with data, and participants with no data at
    any visit, are not coded.

    Returns a list of report lines. Does not modify the harmonized dataset.
    """
    import numpy as np

    lines = []
    w = lines.append

    if harmonized_data is None or harmonized_data.empty:
        return ["[Skip] Harmonized data unavailable; missingness not computed."]

    required = {"cohort", "visit", "studyid"}
    missing_keys = required - set(harmonized_data.columns)
    if missing_keys:
        return [f"[Skip] Missing required columns for availability coding: {sorted(missing_keys)}"]

    df = harmonized_data.copy()
    admin_cols = ["studyid", "cohort", "visit", "hmz_days_since_visit_1"]
    modalities = ["sdoh", "ffq", "health"]
    var_cols = [c for c in df.columns
                if any(m in c for m in modalities) and c not in admin_cols]
    if not var_cols:
        return ["[Skip] No modality variables found."]

    # --- 1. Overall missingness: empty cells over all records, by cohort and visit ---
    overall = (df.groupby("cohort")[var_cols]
                 .apply(lambda g: g.isna().to_numpy().mean() * 100).round(1))
    by_visit = (df.groupby(["cohort", "visit"])[var_cols]
                  .apply(lambda g: g.isna().to_numpy().mean() * 100).round(1))

    # --- 2. Identifiers ---
    df["studyid"] = (df["studyid"].astype(str).str.strip()
                       .str.replace(r"\.0$", "", regex=True))
    bad_id = df["studyid"].isin(["", "nan", "None", "<NA>"])
    dups = df.duplicated(["cohort", "studyid", "visit"], keep=False) & ~bad_id
    if dups.any():
        return [f"[Skip] {int(dups.sum())} duplicated cohort x studyid x visit records; "
                "availability coding not computed."]
    # Records without a studyid cannot be followed across visits; each is its own participant.
    df.loc[bad_id, "studyid"] = "noid_" + df.index[bad_id].astype(str)

    # --- 3. Has data at each visit; one record per participant per visit ---
    vals = df[var_cols]
    df["_has_data"] = (vals.notna() & (vals != 0)).any(axis=1)

    visits = {coh: sorted(g["visit"].dropna().unique()) for coh, g in df.groupby("cohort")}
    people = (df[df["_has_data"]]
              .groupby(["cohort", "studyid"]).size().index.to_frame(index=False))
    grid = pd.concat([people[people["cohort"] == coh].assign(visit=v)
                      for coh, vs in visits.items() for v in vs],
                     ignore_index=True)
    n_no_data_people = int((~df.groupby(["cohort", "studyid"])["_has_data"].any()).sum())

    g = grid.merge(df, on=["cohort", "studyid", "visit"], how="left", indicator=True)
    g["_has_data"] = g["_has_data"].fillna(False).astype(bool)
    n_added = int((g["_merge"] == "left_only").sum())
    g = g.drop(columns="_merge")

    g["_vnum"] = [visits[c].index(v) for c, v in zip(g["cohort"], g["visit"])]
    first_last = (g[g["_has_data"]].groupby(["cohort", "studyid"])["_vnum"]
                    .agg(first="min", last="max").reset_index())
    g = g.merge(first_last, on=["cohort", "studyid"], how="left")

    # --- 4. Codes 0, 1, 2, 3, 5 ---
    administered = (g[g["_has_data"]].groupby(["cohort", "visit"])[var_cols]
                      .apply(lambda x: x.notna().any()))
    codes = np.full((len(g), len(var_cols)), -1, dtype=int)
    empty = g[var_cols].isna().to_numpy()
    has = g["_has_data"].to_numpy()

    for (coh, vis), idx in g.groupby(["cohort", "visit"]).indices.items():
        adm = (administered.loc[(coh, vis)].to_numpy()
               if (coh, vis) in administered.index
               else np.zeros(len(var_cols), dtype=bool))
        h = has[idx][:, None]
        e = empty[idx]
        block = np.full(e.shape, -1, dtype=int)
        block[h & ~e] = 0                    # answered
        block[h & e & ~adm[None, :]] = 1     # not administered
        block[h & e & adm[None, :]] = 3      # unanswered (some become 4 below)
        codes[idx] = block

    later = (g["last"] > g["_vnum"]).to_numpy()
    earlier = (g["first"] < g["_vnum"]).to_numpy()
    codes[~has & earlier & later, :] = 2     # respondent absent
    codes[~has & earlier & ~later, :] = 5    # lost to follow-up

    before_first = ~has & ~earlier           # not yet enrolled: not coded
    n_before_first = int(before_first.sum())
    g = g[~before_first].reset_index(drop=True)
    codes = codes[~before_first]
    if (codes == -1).any():
        return ["[Skip] Some cells could not be coded; availability coding not written."]

    avail = pd.DataFrame(codes, columns=var_cols, index=g.index)

    # --- 5. Survey routing (code 4), applied only to cells currently coded 3 ---
    n_routed, gates_missing = 0, []
    for gate, children in ROUTING.items():
        if gate not in g.columns:
            gates_missing.append(gate)
            continue
        if isinstance(children, str) and children.startswith("prefix:"):
            stem = children.split("prefix:", 1)[1]
            children = [c for c in var_cols if c.startswith(stem)]
        rule, value = ROUTING_SKIP_RULE.get(gate, ("not_equal", 1))
        if rule == "equal":
            skipped = g[gate].notna() & (g[gate] == value)
        else:
            skipped = g[gate].notna() & (g[gate] != value)
        for child in children:
            if child in avail.columns:
                hit = skipped & (avail[child] == 3)
                n_routed += int(hit.sum())
                avail.loc[hit, child] = 4

    for gate, stem in ROUTING_COUNT.items():
        if gate not in g.columns:
            gates_missing.append(gate)
            continue
        for k in range(1, 11):
            child = f"{stem}{k}"
            if child in avail.columns:
                hit = g[gate].notna() & (g[gate] < k) & (avail[child] == 3)
                n_routed += int(hit.sum())
                avail.loc[hit, child] = 4

    avail.insert(0, "visit", g["visit"])
    avail.insert(0, "cohort", g["cohort"])
    avail.insert(0, "studyid", g["studyid"])

    avail_path = os.path.join(output_dir, avail_filename)
    avail.to_csv(avail_path, index=False)

    # --- 6. Summaries for the report ---
    dist = (pd.Series(avail[var_cols].to_numpy().ravel())
              .value_counts(normalize=True).mul(100).round(1)
              .reindex(list(AVAIL_LABELS), fill_value=0.0))

    long = avail.melt(id_vars=["studyid", "cohort", "visit"],
                      var_name="variable", value_name="code")
    tab = long.groupby(["cohort", "visit", "code"]).size().unstack(fill_value=0)
    tab = tab.reindex(columns=list(AVAIL_LABELS), fill_value=0)
    tab = (100 * tab.div(tab.sum(axis=1), axis=0)).round(1)
    tab = tab.rename(columns=AVAIL_LABELS)

    w(f"Variables assessed: {len(var_cols)}")
    w(f"Availability-coded dataset written to: {avail_path}")
    w(f"Records coded: {len(avail)} (records added for visits without a record: {n_added})")
    w(f"Visits before a participant's first visit with data (not coded): {n_before_first}")
    w(f"Participants with no data at any visit (not coded): {n_no_data_people}")
    if gates_missing:
        w(f"Routing gates not present in the data (skipped): {gates_missing}")
    w(f"Cells recoded as routed out: {n_routed}")
    w("")
    w("Overall % of empty cells over all records, by cohort:")
    for coh, val in overall.items():
        w(f" {coh}: {val}")
    w("")
    w("Overall % of empty cells over all records, by cohort and visit:")
    for (coh, vis), val in by_visit.items():
        w(f" {coh} {vis}: {val}")
    w("")
    w("Availability code distribution (% of all coded cells):")
    for code, pct in dist.items():
        w(f" {code} = {AVAIL_LABELS.get(code, 'unknown')}: {pct}")
    w("")
    w("Sources of missingness by cohort and visit (% of coded cells):")
    hdr = list(tab.columns)
    w(" " + "cohort visit".ljust(16) + "".join(str(c).ljust(20) for c in hdr))
    for (coh, vis), row in tab.iterrows():
        w(" " + f"{coh} {vis}".ljust(16) + "".join(f"{row[c]}".ljust(20) for c in hdr))

    return lines



# -----------------------------
# Running Validation
# -----------------------------
def run_validation(harmonized_data: pd.DataFrame):
    cfg = load_config()

    # computing both sections
    dim_lines = _qc_dimensions_and_duplicates_text()
    var_df = _run_variable_checks(harmonized_data, cfg)

    # single text 
    output_dir = os.path.join("data", "output")
    os.makedirs(output_dir, exist_ok=True)

    #  remove any old CSV/XLSX qc tables
    _cleanup_old_qc_artifacts(output_dir)

    report_path = _write_unified_qc_text(dim_lines, var_df, output_dir, harmonized_data=harmonized_data)

    # missingness decomposition, appended to the same report
    miss_lines = _qc_missingness(harmonized_data, output_dir)
    with open(report_path, "a", encoding="utf-8") as f:
        f.write("\nQC REPORT \u2014 Missingness and Availability\n")
        f.write("=" * 72 + "\n")
        for line in miss_lines:
            f.write(str(line) + "\n")
    print(" Missingness section appended to QC report.")

    return report_path, var_df, dim_lines
