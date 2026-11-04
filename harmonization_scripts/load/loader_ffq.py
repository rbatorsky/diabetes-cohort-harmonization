import pandas as pd
import os  

# ---------------------------------------------------------
# Helper Functions 
# ---------------------------------------------------------

INVALID_STUDYIDS = set()  

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

def load_ffq_spanish_data(config):
    global INVALID_STUDYIDS

    df_bprhs_0 = load_table(config["ffq_bprhs_v1"])  
    df_bprhs_2 = load_table(config["ffq_bprhs_v2"])  
    df_bprhs_5 = load_table(config["ffq_bprhs_v3"])  
    df_bprhs_8 = load_table(config["ffq_bprhs_v4"])  

    for df in [df_bprhs_0, df_bprhs_2, df_bprhs_5, df_bprhs_8]:
        df.columns = df.columns.str.lower().str.strip()

    bprhs_dfs = {
        "bprhs_0": df_bprhs_0,
        "bprhs_2": df_bprhs_2,
        "bprhs_5": df_bprhs_5,
        "bprhs_8": df_bprhs_8
    }

    for name, df in bprhs_dfs.items():
        check_duplicates(df, name)

    # PROSPECT FFQ Spanish
    df_prospect = load_table(
        config["ffq_prospect_spanish"],
        encoding='ISO-8859-1'
    )

    # Drop duplicate studyids 
    if 'studyid' in df_prospect.columns:
        dup_mask = df_prospect.duplicated(subset='studyid', keep='first')
        if dup_mask.any():
            df_prospect = df_prospect.loc[~dup_mask].copy()

    df_prospect_nutrients = load_table(
        config["ffq_prospect_perday_full"],
        encoding="latin1")


    for df in list(bprhs_dfs.values()) + [df_prospect, df_prospect_nutrients]:
        df.columns = df.columns.str.lower().str.strip()
        decode_bytes(df)

    # --- Drop invalid studyids 

    INVALID_STUDYIDS = set()

    # 1) invalid == 1 from ffq_prospect_perday_full
    if "invalid" in df_prospect_nutrients.columns:
        df_prospect_nutrients["invalid"] = pd.to_numeric(
            df_prospect_nutrients["invalid"], errors="coerce")

        invalid_from_nutrients = set(
            df_prospect_nutrients.loc[
                df_prospect_nutrients["invalid"] == 1, "studyid"
                ].dropna().unique())

        INVALID_STUDYIDS |= invalid_from_nutrients

        print(
        f"[load_ffq_spanish] Found {len(invalid_from_nutrients)} invalid studyid(s) "
        "from ffq_prospect_perday_full (invalid == 1)." )
    else:
        print("[load_ffq_spanish] WARNING: 'invalid' column not found in ffq_prospect_perday_full.")

    # 2) exclude___1 == 1 from PROSPECT Spanish VISITS file
    df_visits_spanish = load_table(
        config["health_prospect_spanish"],
        encoding="ISO-8859-1")
    
    df_visits_spanish.columns = df_visits_spanish.columns.str.lower().str.strip()
    decode_bytes(df_visits_spanish)

    if "exclude___1" in df_visits_spanish.columns:
        df_visits_spanish["exclude___1"] = pd.to_numeric(
            df_visits_spanish["exclude___1"], errors="coerce")

        invalid_from_exclude = set(
        df_visits_spanish.loc[
            df_visits_spanish["exclude___1"] == 1, "studyid"
        ].dropna().unique())

        INVALID_STUDYIDS |= invalid_from_exclude

        print(
        f"[load_ffq_spanish] Found {len(invalid_from_exclude)} invalid studyid(s) "
        "from PROSPECT4_DATA_SPANISH_VISITS1&2 (exclude___1 == 1).")
    else:
        print(
        "[load_ffq_spanish] WARNING: 'exclude___1' column not found in "
        "health_prospect_spanish.")
        
    # 3) Excluding invalid studyids 
    if INVALID_STUDYIDS:
        before_n = df_prospect_nutrients.shape[0]
        df_prospect_nutrients = df_prospect_nutrients.loc[
            ~df_prospect_nutrients["studyid"].isin(INVALID_STUDYIDS)
            ].copy()
        after_n = df_prospect_nutrients.shape[0]

        # drop from FFQ Spanish
        before_s = df_prospect.shape[0]
        df_prospect = df_prospect.loc[
            ~df_prospect["studyid"].isin(INVALID_STUDYIDS)
            ].copy()
        after_s = df_prospect.shape[0]

        print(
            f"[load_ffq_spanish] Removed {before_n - after_n} rows from ffq_prospect_perday_full "
            f"and {before_s - after_s} rows from ffq_prospect_spanish "
            f"(total unique invalid studyids: {len(INVALID_STUDYIDS)})."
            )

    bprhs_dfs["prospect"] = df_prospect
    bprhs_dfs["prospect_nutrients"] = df_prospect_nutrients

    return bprhs_dfs



# -------------------------------
# English Loader
# -------------------------------

def load_ffq_english_data(config):
    global INVALID_STUDYIDS

    df_eng = load_table(
        config["ffq_prospect_english"],
        encoding='ISO-8859-1'
    )
    decode_bytes(df_eng)

    if INVALID_STUDYIDS and "studyid" in df_eng.columns:
        before = df_eng.shape[0]
        df_eng = df_eng.loc[
            ~df_eng["studyid"].isin(INVALID_STUDYIDS)
        ].copy()
        after = df_eng.shape[0]

        print(
            f"[load_ffq_english] Removed {before - after} invalid studyid rows "
            "from ffq_prospect_english."
        )

    return {"prospect_english": df_eng}


# -------------------------------
# Loader Function
# -------------------------------

def load_ffq_data(config):
    data = {}

    print("Loading Spanish FFQ data...")
    data.update(load_ffq_spanish_data(config))

    print("\nLoading English FFQ data...")
    data.update(load_ffq_english_data(config))

    return data
