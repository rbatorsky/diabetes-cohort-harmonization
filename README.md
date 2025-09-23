# Harmonization Pipeline for BPRHS and PROSPECT Datasets

This repository contains a modular, Python-based harmonization pipeline for the Boston Puerto Rican Health Study (BPRHS) and PROSPECT datasets. The datasets for both the BPRHS and PROSPECT studies should be requested from UMass Lowell and Harvard University. The pipeline starts with a check of the input variables (if variables are missing, a file is generated with the list of missing variables required for the harmonization pipeline to run), then moved to loadind, cleaning, transforming, and merging data across three domains:

- SDOH (Social Determinants of Health)
- Health
- FFQ (Food Frequency Questionnaire)

---

## Project Structure

```
harmonization_pipeline/
│
├── config.yaml                 # User-editable file with paths to raw input data
│
├── harmonization_scripts/
│   ├── main.py                 # Main script to execute the full pipeline
│   ├── config.py               # Loads YAML configuration
│   │
│   ├── check/
│   │   ├── check_variables.py  # Verifies that required variables exist before execution 
│   │   ├── variables.csv       # File listing required variables for each cohort/visit  
│   │   └── __init__.py
│   │
│   ├── load/
│   │   ├── loader_sdoh.py      # Loads and cleans raw SDOH data
│   │   ├── loader_health.py    # Loads and cleans raw Health data
│   │   └── loader_ffq.py       # Loads and cleans raw FFQ data
│   │
│   ├── transform/
│   │   ├── transform_sdoh.py   # Applies transformations for SDOH harmonization
│   │   ├── transform_health.py # Applies transformations for Health harmonization
│   │   └── transform_ffq.py    # Applies transformations for FFQ harmonization
│   │
│   ├── merge/
│   │   └── merge.py            # Merges transformed data into a final harmonized dataset
│   │
│   └── validate/
│       └── validate.py         # Runs validation/quality-control checks on harmonized data
│
├── data/                       #User must include the raw data in the data/raw folder
│   ├── raw/                    # Raw input data (SAS/CSV files)
│   ├── intermediate/           # Cleaned and transformed files
│   └── output/                 # Final merged harmonized dataset + validation reports
│
└── README.md

---

## How to Run the Pipeline

1. Edit the configuration file `config.yaml` at the project root to reflect the correct paths to your raw input files.

2. Run the pipeline:

```
main.py
```

The pipeline will:

- Load paths from `config.yaml`
- Pre-check required variables using `variables.csv` 
- Load and clean raw BPRHS and PROSPECT data
- Apply cleaning and domain-specific transformations
- Merge all harmonized domains
- Save the final file to:
  `data/output/df_hmz_bprhs_prospect_2025.csv`
- Run a validation/quality control check.

---

## Pre-check for Required Variables

Before proceeding with any data transformations, the pipeline performs a validation check to ensure the raw input files contain all necessary variables listed in:

```
harmonization_scripts/check/variables.csv
```

If any variables are missing, the pipeline will raise an error and halt execution. This ensures the harmonization process only runs with valid input data.

---

## Output

The final output is a single harmonized dataset combining BPRHS and PROSPECT data across all domains and visits:

```
data/output/df_hmz_bprhs_prospect_2025.csv
```

---

## Contact

For questions, feedback, or contributions, please contact:

- Rebecca Batorsky  
- Andreia Martinho  
TIAI, Tufts University
