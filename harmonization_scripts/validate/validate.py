import os
import glob
import pandas as pd
from harmonization_scripts.config import load_config
from harmonization_scripts.load.loader_health import load_health_spanish_data
from harmonization_scripts.load.loader_ffq import load_ffq_spanish_data


CLEANUP_OLD_QC_TABLES = True


def _to(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)


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
        "data/raw/prospect/PROSPECT4a_DATA_ENGLISH_VISITS1&2_2024-11-26_1523.csv"
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
        "data/raw/prospect/PROSPECT5aFFQ_English_raw_09MAY2024(in).csv"
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

    merged_path = os.path.join(out_dir, "df_hmz_bprhs_prospect_2025.csv")
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

    key_cols = {'studyid', 'cohort', 'visit'}
    sdoh_cols = set().union(*(df.columns for df in df_sdoh)) if df_sdoh else set()
    health_cols = set().union(*(df.columns for df in df_health)) if df_health else set()
    ffq_cols = set().union(*(df.columns for df in df_ffq)) if df_ffq else set()
    merged_cols = set(df_hmz.columns)

    overlap_sdoh_health = (sdoh_cols & health_cols) - key_cols
    overlap_sdoh_ffq = (sdoh_cols & ffq_cols) - key_cols
    overlap_health_ffq = (health_cols & ffq_cols) - key_cols

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

    keys_sdoh   = collect_keys(df_sdoh)
    keys_health = collect_keys(df_health)
    keys_ffq    = collect_keys(df_ffq)

    union_keys = pd.concat([keys_sdoh, keys_health, keys_ffq], ignore_index=True).drop_duplicates() \
                  if not (keys_sdoh.empty and keys_health.empty and keys_ffq.empty) \
                  else pd.DataFrame(columns=['studyid','cohort','visit'])
    merged_keys = df_hmz[['studyid','cohort','visit']].drop_duplicates()

    u_set = set(map(tuple, union_keys[['studyid','cohort','visit']].values)) if not union_keys.empty else set()
    m_set = set(map(tuple, merged_keys[['studyid','cohort','visit']].values))

    missing_in_merged = list(u_set - m_set)
    added_in_merged   = list(m_set - u_set)

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
    w(f"Final merged dataset: {os.path.join('data','output','df_hmz_bprhs_prospect_2025.csv')}")
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
    if overlap_sdoh_health or overlap_sdoh_ffq or overlap_health_ffq:
        w("Overlapping non-key columns across domains:")
        if overlap_sdoh_health: w(f"  SDOH ∩ Health: {sorted(overlap_sdoh_health)}")
        if overlap_sdoh_ffq:    w(f"  SDOH ∩ FFQ:    {sorted(overlap_sdoh_ffq)}")
        if overlap_health_ffq:  w(f"  Health ∩ FFQ:  {sorted(overlap_health_ffq)}")
    else:
        w("No overlapping non-key columns across domains.")
    w("")
    w("Key integrity:")
    w(f"  Null studyid: {null_studyid}")
    w(f"  Null cohort:  {null_cohort}")
    w(f"  Null visit:   {null_visit}")
    w("  Counts by (cohort, visit):")
    for c, v, n in counts_cv:
        w(f"    {c} {v}: {n}")

    w("")
    if not u_set:
        w("Key reconciliation: skipped (no intermediate files with studyid/cohort/visit).")
    else:
        w("Key reconciliation (union of domain keys ↔ merged keys):")
        w(f"  Union keys (inputs): {len(u_set)}")
        w(f"  Merged keys:         {len(m_set)}")
        if missing_in_merged:
            w(f"  WARNING: {len(missing_in_merged)} keys present in inputs but missing in merged. Examples: {missing_in_merged[:10]}")
        else:
            w("  No keys missing from merged relative to inputs.")
        if added_in_merged:
            w(f"  WARNING: {len(added_in_merged)} keys present in merged but not found in inputs. Examples: {added_in_merged[:10]}")
        else:
            w("  No unexpected extra keys in merged relative to inputs.")

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
    ]
    checks_ffq = [
        ("BPRHS",    "v1", "bprhs_0",  "supdur_1",    "hmz_ffq_sup_dur_1"),
        ("PROSPECT", "v1", "prospect", "supdur_1",    "hmz_ffq_sup_dur_1"),
    ]

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
        "domain","cohort","visit","hmz_var","raw_var",
        "hmz_missing","raw_missing","hmz_non_numeric","raw_non_numeric",
        "hmz_mean","raw_mean","hmz_std","raw_std","n_hmz","n_raw"
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

    # ---------- Additional Checks (compact) -----------
    extra_lines = []
    x = extra_lines.append

    if isinstance(harmonized_data, pd.DataFrame) and not harmonized_data.empty:
        df = harmonized_data

        expected_vars = ["hmz_sdoh_age", "hmz_health_lab_a1c", "hmz_ffq_sup_dur_1"]
        missing_expected = [v for v in expected_vars if v not in df.columns]
        x("Structural — Expected variable presence:")
        x(f"  Missing expected hmz_ variables: {missing_expected if missing_expected else 'none'}")

        n_num = df.select_dtypes(include=['number']).shape[1]
        n_non = df.shape[1] - n_num
        x("Structural — Dtype summary:")
        x(f"  Numeric columns: {n_num} | Non-numeric columns: {n_non}")

        miss = df.isna().mean().sort_values(ascending=False)
        top10 = miss.head(10)
        if top10.shape[0] > 0:
            x("Structural — Top 10 missingness (fraction):")
            for k, v in top10.items():
                x(f"  {k}: {round(float(v),3)}")

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

    if isinstance(var_df, pd.DataFrame) and not var_df.empty:
        x("Cross-dataset — HMZ vs RAW consistency flags:")
        flags = []
        for _, r in var_df.iterrows():
            hm = r.get("hmz_mean", None)
            rw = r.get("raw_mean", None)
            if pd.notna(hm) and pd.notna(rw):
                diff = abs(float(hm) - float(rw))
                rel  = diff / (abs(float(rw)) + 1e-9)
                if (diff > 0.1) and (rel > 0.05):
                    flags.append(f"{r['domain']} {r['cohort']} {r['visit']} {r['hmz_var']} vs {r['raw_var']}: "
                                 f"mean diff={round(diff,3)} (rel={round(rel*100,1)}%) — check transformation/scale.")
            hm_miss = r.get("hmz_missing", None)
            rw_miss = r.get("raw_missing", None)
            n_h     = r.get("n_hmz", None)
            n_r     = r.get("n_raw", None)
            if all(pd.notna(v) for v in [hm_miss, rw_miss, n_h, n_r]) and n_h and n_r:
                hm_rate = float(hm_miss)/max(int(n_h),1)
                rw_rate = float(rw_miss)/max(int(n_r),1)
                if abs(hm_rate - rw_rate) > 0.10:
                    flags.append(f"{r['domain']} {r['cohort']} {r['visit']} {r['hmz_var']} vs {r['raw_var']}: "
                                 f"missing gap={round((hm_rate-rw_rate)*100,1)} pp")
            nn_h = int(r.get("hmz_non_numeric", 0) or 0)
            nn_r = int(r.get("raw_non_numeric", 0) or 0)
            if nn_h > 0 or nn_r > 0:
                flags.append(
                    f"{r['domain']} {r['cohort']} {r['visit']} {r['hmz_var']} vs {r['raw_var']}: "
                    f"non-numeric → HMZ={nn_h}, RAW={nn_r}"
                )
            if pd.notna(n_h) and pd.notna(n_r) and int(n_h) != int(n_r):
                flags.append(f"{r['domain']} {r['cohort']} {r['visit']} {r['hmz_var']} vs {r['raw_var']}: "
                             f"n mismatch HMZ={int(n_h)} RAW={int(n_r)}")
        if flags:
            for line in flags[:30]:
                x("  " + line)
            if len(flags) > 30:
                x(f"  ... and {len(flags)-30} more")
        else:
            x("  No material differences flagged by thresholds (0.1 abs & 5% rel; 10pp missing).")

    # -------------- write file --------------
    with open(path, "w", encoding="utf-8") as f:
        # Dimensions section
        f.write("QC REPORT — Dimensions & Duplicates\n")
        f.write("=" * 72 + "\n")
        for line in dim_lines:
            f.write(str(line) + "\n")

        # Variable checks section (table)
        f.write("\nQC REPORT — Variable Checks\n")
        f.write("=" * 72 + "\n")
        if var_df.empty:
            f.write("(no variable checks)\n")
        else:
            f.write(header_line + "\n")
            f.write(sep_line + "\n")
            for _, row in var_df.iterrows():
                f.write(row_to_line(row.to_dict()) + "\n")

        # Additional checks
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
# Running Validation
# -----------------------------
def run_validation(harmonized_data: pd.DataFrame):
    cfg = load_config()

    # compute both sections
    dim_lines = _qc_dimensions_and_duplicates_text()
    var_df = _run_variable_checks(harmonized_data, cfg)

    # single text 
    output_dir = os.path.join("data", "output")
    os.makedirs(output_dir, exist_ok=True)

    #  remove any old CSV/XLSX qc tables
    _cleanup_old_qc_artifacts(output_dir)

    report_path = _write_unified_qc_text(dim_lines, var_df, output_dir, harmonized_data=harmonized_data)
    return report_path, var_df, dim_lines
