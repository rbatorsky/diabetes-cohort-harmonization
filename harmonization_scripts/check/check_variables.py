import os
import pandas as pd
import pyreadstat

def check_required_variables(config):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    variables_path = os.path.join(project_root, "scripts", "check", "variables.csv")

    if not os.path.exists(variables_path):
        raise FileNotFoundError(f"Missing variables.csv at: {variables_path}")

    required_df = pd.read_csv(variables_path)

    # Mapping each column to one or more source files
    source_map = {
        "source_variable_bprhs_v1": [config["bprhs_v1"], config["ffq_bprhs_v1"]],
        "source_variable_bprhs_v2": [config["bprhs_v2"], config["ffq_bprhs_v2"]],
        "source_variable_bprhs_v3": [config["bprhs_v3"], config["ffq_bprhs_v3"]],
        "source_variable_bprhs_v4": [config["bprhs_v4"], config["ffq_bprhs_v4"]],
        "source_variable_prospect": [
            config["ffq_prospect_spanish"],
            config["ffq_prospect_english"],
            config["ffq_prospect_perday_full"],
            config["ffq_prospect_perday_v1"],
            config["ffq_prospect_perday_v2"],
            config["ffq_prospect_perday_v3"],
            config["ffq_prospect_perday_v4"],
            config["health_prospect_spanish"],
            config["health_prospect_english"],
            config["sdoh_prospect_spanish"],
            config["sdoh_prospect_english"]
        ]
    }

    for column_name, file_paths in source_map.items():
        all_columns = set()

        print(f"\nChecking required variables for '{column_name}' in {len(file_paths)} file(s)...")

        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"  [Missing file] {file_path}")
                continue

            try:
                if file_path.endswith(".csv"):
                    df = pd.read_csv(file_path, nrows=0)
                elif file_path.endswith(".sas7bdat"):
                    df, _ = pyreadstat.read_sas7bdat(file_path, metadataonly=True)
                else:
                    print(f"  [Skipped file type] {file_path}")
                    continue

                # Normalize column names
                normalized_columns = {col.strip().lower() for col in df.columns}
                all_columns.update(normalized_columns)
            except Exception as e:
                print(f"  [Error reading] {file_path} → {e}")
                continue

        # Normalize required variables
        required_vars = required_df[column_name].dropna().tolist()
        normalized_required = [(var, var.strip().lower()) for var in required_vars]

        # Compare
        missing_vars = [orig for orig, norm in normalized_required if norm not in all_columns]

        if missing_vars:
            print(f"\n  Missing {len(missing_vars)} variable(s) in '{column_name}':")
            for var in missing_vars:
                print(f"    - {var}")

            output_file = os.path.join(project_root, f"missing_vars_{column_name}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"Missing variables for {column_name}:\n\n")
                for var in missing_vars:
                    f.write(f"{var}\n")

            raise ValueError(
                f"{len(missing_vars)} variables are missing for {column_name}. "
                f"See file: {output_file}"
            )
        else:
            print(f"  All required variables found for '{column_name}'.")
