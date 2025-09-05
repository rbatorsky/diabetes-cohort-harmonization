import argparse
import os
import pandas as pd
import sys

def ffq_perday_hmz(manifest_path, output_dir, col, source, visit_name, cohort):
    # Strip spaces from col input
    col = col.replace(" ", "")

    # Load manifest and create a mapping from type to name
    manifest_df = pd.read_excel(manifest_path)
    manifest_kv = dict(zip(manifest_df['type'], manifest_df['name']))

    # Load data
    if cohort == "PROSPECT":
        pr_cols_to_rm = ["batch", "invalid", "SUB_NAME", "Sub_id"]
        data_perday_perfood = pd.read_csv(manifest_kv[source],encoding="latin1")
        data_perday_perfood = data_perday_perfood.drop(columns=[c for c in pr_cols_to_rm if c in data_perday_perfood.columns], errors='ignore')

        # Filter and aggregate numeric columns by studyid
        visit_clean = visit_name.lstrip("v")
        data_perfood_df = (
            data_perday_perfood[data_perday_perfood['visit'].astype(str) == visit_clean]
            .groupby("studyid", as_index=False)
            .sum(numeric_only=True)
        )
    else:
        data_perfood_df = pd.read_excel(manifest_kv[source])

    # Lowercase column names
    data_perfood_df.columns = [c.lower() for c in data_perfood_df.columns]

    # Load metadata and strip spaces from column names
    metadata = pd.read_excel(manifest_kv["metadata"])
    metadata.columns = [c.replace(" ", "") for c in metadata.columns]

    # Filter metadata using cleaned 'col'
    if col not in metadata.columns:
        raise ValueError(f"Column '{col}' not found in metadata columns: {metadata.columns.tolist()}")
    if "variable_name" not in metadata.columns:
        raise ValueError("Column 'variable_name' is missing in metadata")

    metadata = metadata[[col, "variable_name"]].dropna(subset=[col, "variable_name"])

    # Find intersection of columns
    cols_to_select = list(set(metadata[col]) & set(data_perfood_df.columns))
    metadata = metadata[metadata[col].isin(cols_to_select)]

    # Select and rename columns
    data_perfood_df = data_perfood_df[["studyid"] + cols_to_select]
    rename_dict = dict(zip(metadata[col], metadata["variable_name"]))
    data_perfood_df = data_perfood_df.rename(columns=rename_dict)

    # Add cohort and visit
    data_perfood_df["cohort"] = cohort
    data_perfood_df["visit"] = visit_name

    # Write output
    outfile = os.path.join(output_dir, f"{source}_{visit_name}_hmz_23jul25_py.csv")
    data_perfood_df.to_csv(outfile, index=False)

    return data_perfood_df


def main():
    parser = argparse.ArgumentParser(description="Generate harmonized FFQ data")
    parser.add_argument("--manifest", required=True, help="Manifest File")
    parser.add_argument("--output_dir", required=True, help="Output Directory")
    
    # If no arguments are supplied, print help and exit
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()

    manifest = args.manifest
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Run harmonization
    print("Harmonizing BPRHS FFQ v1")
    b1 = ffq_perday_hmz(manifest, output_dir, "source_variable_bprhs_v1", "bprhs_v1_ffq", "v1", "BPRHS")
    print(b1.shape)

    print("Harmonizing BPRHS FFQ v2")
    b2 = ffq_perday_hmz(manifest, output_dir, "source_variable_bprhs_v2", "bprhs_v2_ffq", "v2", "BPRHS")
    print(b2.shape)

    print("Harmonizing BPRHS FFQ v3")
    b3 = ffq_perday_hmz(manifest, output_dir, "source_variable_bprhs_v3", "bprhs_v3_ffq", "v3", "BPRHS")
    print(b3.shape)

    print("Harmonizing BPRHS FFQ v4")
    b4 = ffq_perday_hmz(manifest, output_dir, "source_variable_bprhs_v4", "bprhs_v4_ffq", "v4", "BPRHS")
    print(b4.shape)

    print("Harmonizing PROSPECT v1")
    p1 = ffq_perday_hmz(manifest, output_dir, "source_variable_prospect", "prospect_ffq", "v1", "PROSPECT")
    print(p1.shape)

    print("Harmonizing PROSPECT v2")
    p2 = ffq_perday_hmz(manifest, output_dir, "source_variable_prospect", "prospect_ffq", "v2", "PROSPECT")
    print(p2.shape)

    # Find common columns across all datasets
    common_cols = set(b1.columns)
    for df in [b2, b3, b4, p1, p2]:
        common_cols &= set(df.columns)
    common_cols = list(common_cols)

    # Combine all dataframes
    combined_df = pd.concat([
        b1[common_cols],
        b2[common_cols],
        b3[common_cols],
        b4[common_cols],
        p1[common_cols],
        p2[common_cols]
    ], ignore_index=True)

    print(combined_df.shape)
    output_file = os.path.join(output_dir, "harmonize_bpr_prospect_ffq.csv")
    combined_df.to_csv(output_file, index=False)
    print(f"Writing combined harmonization file to {output_file}")


if __name__ == "__main__":
    main()