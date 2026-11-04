
import pandas as pd
import os

# ---------------------------------------------------------
# Helper Functions 
# ---------------------------------------------------------

def decode_bytes(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(
                lambda x: x.decode('utf-8', 'ignore') if isinstance(x, bytes) else x
            )
    return df

def check_duplicates(df, name):
    if 'studyid' in df.columns:
        duplicates = df[df.duplicated(subset='studyid', keep=False)]
        if not duplicates.empty:
            print(f"\nDuplicate studyids in {name}:")
            print(duplicates['studyid'].value_counts())
        else:
            print(f"\nNo duplicates in {name}.")
    else:
        print(f"\nNo 'studyid' column in {name}.")


def load_table(path, **csv_kwargs):

    ext = os.path.splitext(path)[1].lower()

    if ext in [".sas7bdat", ".xpt"]:
        df = pd.read_sas(path)
    elif ext == ".csv":
        df = pd.read_csv(path, **csv_kwargs)
    else:
        raise ValueError(f"Unsupported file extension '{ext}' for path: {path}")

    return df


# -------------------------------
# Spanish Loader
# -------------------------------

def load_health_spanish_data(config):
    df_bprhs_0 = load_table(config["bprhs_v1"])
    df_bprhs_2 = load_table(config["bprhs_v2"])
    df_bprhs_5 = load_table(config["bprhs_v3"])
    df_bprhs_8 = load_table(config["bprhs_v4"])

    for df in [df_bprhs_0, df_bprhs_2, df_bprhs_5, df_bprhs_8]:
        df.columns = df.columns.str.lower().str.strip()

    bprhs_dfs = {
        "bprhs_0": df_bprhs_0,
        "bprhs_2": df_bprhs_2,
        "bprhs_5": df_bprhs_5,
        "bprhs_8": df_bprhs_8
    }

    # Check duplicates before dropping
    for name, df in bprhs_dfs.items():
        check_duplicates(df, name)

    # Drop duplicate studyids in 8-year BPRHS if present
    if 'studyid' in df_bprhs_8.columns:
        dup_mask = df_bprhs_8.duplicated(subset='studyid', keep='first')
        n_dropped = dup_mask.sum()
        if n_dropped > 0:
            print(f"\n[bprhs_8] Dropping {n_dropped} duplicate row(s) based on studyid (keeping first occurrence).")
            df_bprhs_8 = df_bprhs_8.loc[~dup_mask].copy()
    bprhs_dfs["bprhs_8"] = df_bprhs_8

    # Check duplicates again after cleaning
    for name, df in bprhs_dfs.items():
        check_duplicates(df, name)

    # PROSPECT health Spanish: can be CSV or SAS depending on config
    df_prospect = load_table(
        config["health_prospect_spanish"],
        encoding='ISO-8859-1')

    # Excluding invalid studyids
    if {"studyid", "exclude___1", "redcap_event_name"}.issubset(df_prospect.columns):
        before = len(df_prospect)

        ev = df_prospect["redcap_event_name"].astype(str).str.lower()
        base_mask = df_prospect["exclude___1"] == 1

        # baseline_arm_1 → PROSPECT visit 1
        # visit_2_arm_1  → PROSPECT visit 2
        v1_mask = base_mask & ev.str.contains("baseline_arm_1")
        v2_mask = base_mask & ev.str.contains("visit_2_arm_1")

        drop_mask = v1_mask | v2_mask
        df_prospect = df_prospect.loc[~drop_mask].copy()

        dropped = before - len(df_prospect)
        print(f"[load_health_spanish] Excluded {dropped} PROSPECT health row(s) based on exclude___1.")
    else:
        print("[load_health_spanish] WARNING: exclude___1 / redcap_event_name not found in PROSPECT health file.")

    print(f"\nTotal studyid entries: {df_prospect['studyid'].count()}")
    print(f"Unique studyid entries: {df_prospect['studyid'].nunique()}")
    dup = df_prospect['studyid'][df_prospect['studyid'].duplicated(keep=False)]
    print(f"Total duplicate rows: {dup.count()} | Unique: {dup.nunique()}")
    print(dup.value_counts().head())

    # Decode bytes for all BPRHS + PROSPECT
    for df in list(bprhs_dfs.values()) + [df_prospect]:
        decode_bytes(df)

    bprhs_dfs["prospect"] = df_prospect
    return bprhs_dfs


# -------------------------------
# English Loader
# -------------------------------

def load_health_english_data(config):
    df_eng = load_table(
        config["health_prospect_english"],
        encoding='ISO-8859-1')

    print(f"\nTotal studyid entries: {df_eng['studyid'].count()}")
    print(f"Unique studyid entries: {df_eng['studyid'].nunique()}")
    dup = df_eng['studyid'][df_eng['studyid'].duplicated(keep=False)]
    print(f"Total duplicate rows: {dup.count()} | Unique: {dup.nunique()}")
    print(dup.value_counts().head())

    decode_bytes(df_eng)
    return {"prospect_english": df_eng}


# -------------------------------
# Loader Function
# -------------------------------

def load_health_data(config):
    data = {}

    print("Loading Spanish health data...")
    data.update(load_health_spanish_data(config))

    print("\nLoading English health data...")
    data.update(load_health_english_data(config))

    return data
