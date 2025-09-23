import os
import pandas as pd

def assign_cohort_and_visit(df_name, df):
    cohort, visit = None, None
    if "bprhs" in df_name:
        if "_0" in df_name: cohort, visit = "BPRHS", "v1"
        elif "_2" in df_name: cohort, visit = "BPRHS", "v2"
        elif "_5" in df_name: cohort, visit = "BPRHS", "v3"
        elif "_8" in df_name: cohort, visit = "BPRHS", "v4"
    elif "prospect" in df_name:
        if "visit_1" in df_name: cohort, visit = "PROSPECT", "v1"
        elif "visit_2" in df_name: cohort, visit = "PROSPECT", "v2"
    if df is not None:
        df["cohort"] = cohort
        df["visit"] = visit
    return df

def strip_suffixes(df, suffix):
    if df is not None:
        return df.rename(columns={col: col.replace(suffix, "") for col in df.columns if col != "studyid"})
    return df

def drop_redundant_columns(df_list):
    cols_to_drop = [
        "hmz_visit", "hmz_record_id",
        "hmz_visit_prospect", "hmz_record_id_prospect",
        "hmz_record_id_prospect_x", "hmz_record_id_prospect_y"
    ]
    return [df.drop(columns=cols_to_drop, errors="ignore") for df in df_list]

def process_transformed_data(transformed_data):
    suffix_map = {
        "_bprhs_0": "_bprhs_0", "_bprhs_2": "_bprhs_2",
        "_bprhs_5": "_bprhs_5", "_bprhs_8": "_bprhs_8",
        "_prospect_visit_1": "_prospect_v1", "_prospect_visit_2": "_prospect_v2",
        "_prospect_english_visit_1": "_prospect_v1", "_prospect_english_visit_2": "_prospect_v2"
    }

    for domain in ["sdoh", "health", "ffq"]:
        cleaned = {}
        for name, df in transformed_data[domain].items():
            for key, suffix in suffix_map.items():
                if key in name:
                    df = strip_suffixes(df, suffix)
            cleaned[name] = df
        transformed_data[domain] = cleaned

    return transformed_data

def inspect_key_multiples(df, label):
    if all(col in df.columns for col in ['studyid', 'cohort', 'visit']):
        duplicated = df.duplicated(subset=['studyid', 'cohort', 'visit'], keep=False)
        if duplicated.any():
            print(f"[{label}] WARNING: Found multiple rows per key combination!")
            print(df.loc[duplicated, ['studyid', 'cohort', 'visit']].value_counts())
        else:
            print(f"[{label}] Keys (studyid, cohort, visit) are unique.")
    else:
        print(f"[{label}] Skipped key inspection - missing key columns.")

def merge_transformed_data(transformed_data):
    transformed_data = process_transformed_data(transformed_data)

    # Apply cohort/visit assignment BEFORE inspections
    df_sdoh = [assign_cohort_and_visit(name, df) for name, df in transformed_data["sdoh"].items()]
    df_health = [assign_cohort_and_visit(name, df) for name, df in transformed_data["health"].items()]
    df_ffq = [assign_cohort_and_visit(name, df) for name, df in transformed_data["ffq"].items()]
 
    df_sdoh = drop_redundant_columns(df_sdoh)
    df_health = drop_redundant_columns(df_health)
    df_ffq = drop_redundant_columns(df_ffq)

    print("Inspecting uniqueness BEFORE merging:")
    for df, label in zip([df_sdoh, df_health, df_ffq], ['SDOH', 'Health', 'FFQ']):
        combined = pd.concat(df, ignore_index=True)
        inspect_key_multiples(combined, label)

    merged_df_sdoh = pd.concat(df_sdoh, ignore_index=True)
    merged_df_health = pd.concat(df_health, ignore_index=True)
    merged_df_ffq = pd.concat(df_ffq, ignore_index=True)
    
    print("merged_df_sdoh dtypes:\n", merged_df_sdoh.dtypes[['studyid', 'cohort', 'visit']])
    print("merged_df_health dtypes:\n", merged_df_health.dtypes[['studyid', 'cohort', 'visit']])
    print("merged_df_ffq dtypes:\n", merged_df_ffq.dtypes[['studyid', 'cohort', 'visit']])


    merged_df = merged_df_sdoh.merge(merged_df_health, on=["studyid", "cohort", "visit"], how="outer")
    hmz_df = merged_df.merge(merged_df_ffq, on=["studyid", "cohort", "visit"], how="outer")

    print("Inspecting uniqueness AFTER merging:")
    inspect_key_multiples(hmz_df, "Final merged")

    output_dir = os.path.join("data", "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "df_hmz_bprhs_prospect_2025.csv")
    hmz_df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Final merged dataset shape: {hmz_df.shape}")
    print(f"Final merged dataset saved to {output_path}")
    return hmz_df
