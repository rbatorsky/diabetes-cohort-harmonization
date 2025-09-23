
import pandas as pd

# ---------------------------------------------------------
# Helper Functions (decoding bytes and checking duplicates)
# ---------------------------------------------------------

def decode_bytes(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: x.decode('utf-8', 'ignore') if isinstance(x, bytes) else x)
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

# -------------------------------
# Spanish Loader
# -------------------------------

def load_ffq_spanish_data(config):
    df_bprhs_0 = pd.read_sas(config["ffq_bprhs_v1"])
    df_bprhs_2 = pd.read_sas(config["ffq_bprhs_v2"])
    df_bprhs_5 = pd.read_sas(config["ffq_bprhs_v3"])
    df_bprhs_8 = pd.read_sas(config["ffq_bprhs_v4"])

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

    df_prospect = pd.read_csv(config["ffq_prospect_spanish"], encoding='ISO-8859-1')

    print(f"\nTotal studyid entries: {df_prospect['studyid'].count()}")
    print(f"Unique studyid entries: {df_prospect['studyid'].nunique()}")
    dup = df_prospect['studyid'][df_prospect['studyid'].duplicated(keep=False)]
    print(f"Total duplicate rows: {dup.count()} | Unique: {dup.nunique()}")
    print(dup.value_counts().head())

    # Drop known duplicates
    duplicate_ids = [842101149.0, 866101456.0]
    for studyid in duplicate_ids:
        idx = df_prospect[df_prospect['studyid'] == studyid].index
        if len(idx) > 1:
            df_prospect = df_prospect.drop(idx[1:])

    # Load nutrient-level PROSPECT FFQ
    df_prospect_nutrients = pd.read_csv(config["ffq_prospect_perday_full"], encoding='latin1')

    # Lowercase + decode everything
    for df in list(bprhs_dfs.values()) + [df_prospect, df_prospect_nutrients]:
        df.columns = df.columns.str.lower().str.strip()
        decode_bytes(df)

    bprhs_dfs["prospect"] = df_prospect
    bprhs_dfs["prospect_nutrients"] = df_prospect_nutrients
    return bprhs_dfs

# -------------------------------
# English Loader
# -------------------------------

def load_ffq_english_data(config):
    df_eng = pd.read_csv(config["ffq_prospect_english"], encoding='ISO-8859-1')
    decode_bytes(df_eng)
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
