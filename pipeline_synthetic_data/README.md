1. Harmonization Pipeline for BPRHS and PROSPECT Datasets

1.1 Overview
This repository contains a modular, Python-based harmonization pipeline for the Boston Puerto Rican Health Study (BPRHS) and PROSPECT datasets. The datasets for both the BPRHS and PROSPECT studies should be requested from UMass Lowell and Harvard University. Once users obtain the datasets, they should update the paths in the config.yaml file. The pipeline starts with a check of the input variables (if variables are missing, a file is generated with the list of missing variables required for the harmonization pipeline to run), then loads, cleans, transforms, and merges data across three domains: (i) SDOH (Social Determinants of Health), (ii) Health, and (iii) FFQ (Food Frequency Questionnaire). 


1.2. Input data
1.2.1. BPRHS datasets 

The BPRHS datasets used in the harmonization pipeline (information about these datasets is provided below) can be requested through the University of Massachusetts Lowell (UMass Lowell) by submitting a CPH Analysis and Data Request Proposal Form, which is available at https://www.uml.edu/research/uml-cph/research/BPRHS/. The corresponding BPRHS codebooks are available at https://www.uml.edu/research/uml-cph/research/BPRHS/. 

bprhs_v1: data/raw/bprhs/fullbaseline_03jan2018.sas7bdat
ffq_bprhs_v1: data/raw/bprhs/baseline_ffq_per_day_011922.sas7bdat

bprhs_v2: data/raw/bprhs/full2yr_19nov2018.sas7bdat
ffq_bprhs_v2: data/raw/bprhs/twoyear_ffq_per_day_011922.sas7bdat

bprhs_v3: data/raw/bprhs/released_5yr_bprhs_07dec23.sas7bdat
ffq_bprhs_v3: data/raw/bprhs/fiveyear_ffq_per_day_062223.sas7bdat

bprhs_v4: data/raw/bprhs/released_8yr_010424.sas7bdat
ffq_bprhs_v4: data/raw/bprhs/eightyear_ffq_per_day_121323.sas7bdat

1.2.2. PROSPECT datasets

The PROSPECT datasets used in the harmonization pipeline (information about these datasets is provided below) can be requested through Harvard University by submitting a Proposal Form, which is available at https://hsph.harvard.edu/research/puerto-rico-PROSPECT/data-requests/. 

health_prospect_spanish and sdoh_prospect_spanish: data/raw/prospect/PROSPECT4_DATA_SPANISH_VISITS1&2__2024-11-26_1522.csv
health_prospect_english and sdoh_prospect_english: data/raw/prospect/PROSPECT4a_DATA_ENGLISH_VISITS1&2_2024-11-26_1523.csv

ffq_prospect_spanish: data/raw/prospect/PROSPECT5FFQ_Spanish_raw_09MAY2024(in).csv
ffq_prospect_english: data/raw/prospect/PROSPECT5aFFQ_English_raw_09MAY2024(in).csv
ffq_prospect_perday_full: data/raw/prospect/ffq_perday_perfood659_all_copy_Tufts.csv

1.3. Synthetic data 
Synthetic datasets are provided to test the pipeline without access to the original data. They have the same file structure, variable names and variable types as the original files listed above, and include 100 randomly selected participants from BPRHS and from each PROSPECT clinic file, each with a synthetic identifier that is consistent across files and visits. Numeric variables were drawn from normal distributions defined by the means and standard deviations of the original variables, truncated to their observed ranges; categorical variables were drawn according to the observed category proportions; and dates were randomly shifted by up to 30 days. Names and categorical values occurring fewer than 10 times in the original data (such as free-text responses) were replaced by a placeholder, and structural variables such as the visit indicator were retained unchanged. Because variables were generated independently, the synthetic data are intended for testing the pipeline only, not for analysis.

The config.yaml file in this pipeline points to the synthetic files listed below. Users with access to the original BPRHS and PROSPECT data should replace these paths with the paths to the original files (section 1.2).


1.3.1. BPRHS Synthetic Files
bprhs_v1: data/raw/bprhs/synthetic_fullbaseline_03jan2018.csv
bprhs_v2: data/raw/bprhs/synthetic_full2yr_19nov2018.csv
bprhs_v3: data/raw/bprhs/synthetic_released_5yr_bprhs_07dec23.csv
bprhs_v4: data/raw/bprhs/synthetic_released_8yr_010424.csv

ffq_bprhs_v1: data/raw/bprhs/synthetic_baseline_ffq_per_day_011922.csv
ffq_bprhs_v2: data/raw/bprhs/synthetic_twoyear_ffq_per_day_011922.csv
ffq_bprhs_v3: data/raw/bprhs/synthetic_fiveyear_ffq_per_day_062223.csv
ffq_bprhs_v4: data/raw/bprhs/synthetic_eightyear_ffq_per_day_121323.csv



1.3.2. PROSPECT Synthetic Files
FFQ raw data files
ffq_prospect_spanish: data/raw/prospect/synthetic_PROSPECT5FFQ_Spanish_raw_09MAY2024(in).csv
ffq_prospect_english: data/raw/prospect/synthetic_PROSPECT5aFFQ_English_raw_09MAY2024(in).csv
ffq_prospect_perday_full: data/raw/prospect/synthetic_ffq_perday_perfood659_all_copy_Tufts.csv

Health raw data
health_prospect_spanish: data/raw/prospect/synthetic_PROSPECT4_DATA_SPANISH_VISITS1&2__2024-11-26_1522.csv
health_prospect_english: data/raw/prospect/synthetic_PROSPECT4a_DATA_ENGLISH_VISITS1&2_2024-11-26_1523.csv

SDOH raw data
sdoh_prospect_spanish: data/raw/prospect/synthetic_PROSPECT4_DATA_SPANISH_VISITS1&2__2024-11-26_1522.csv
sdoh_prospect_english: data/raw/prospect/synthetic_PROSPECT4a_DATA_ENGLISH_VISITS1&2_2024-11-26_1523.csv



1.4 Harmonization Pipeline in Python
1.4.1 Requirements for running the pipeline
1.4.1.1 Python
Python 3.10 or newer

1.4.1.2 Libraries (listed in requirements.txt)
- pandas
- numpy
- pyreadstat
- pyyaml

1.4.2. Installation

1.4.2.1. Download the repository (clone it with git) and go to this pipeline's folder:

    git clone https://github.com/rbatorsky/diabetes-cohort-harmonization.git
    cd diabetes-cohort-harmonization/pipeline_synthetic_data

The repository contains two versions of the pipeline: pipeline_synthetic_data/ (ready to run with the included synthetic data) and pipeline/ (for the original data). All following steps are run from inside the chosen folder.

1.4.2.2. Create and activate a virtual environment (Python 3.10 or newer):

    python3 -m venv venv
    source venv/bin/activate        (Mac/Linux)
    venv\Scripts\activate           (Windows)

1.4.2.3. Install the required libraries:

    pip install -r requirements.txt


1.4.3. Pipeline structure

```
pipeline_synthetic_data/
│── main.py                     # Main script to execute the full pipeline
├── config.yaml                 # User-editable file with paths to raw input data
├── requirements.txt            # Required Python libraries
│
├── harmonization_scripts/
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
├── data/                       # Synthetic input files are included in data/raw
│   ├── raw/                    # Raw input data (SAS/CSV files)
│   ├── intermediate/           # Cleaned and transformed files
│   └── output/                 # Final merged harmonized dataset + validation reports
│
└── README.md

---

1.4.4. Running the Pipeline


1.4.4.1. The synthetic input files are included in data/raw/bprhs/ and data/raw/prospect/, and config.yaml points to them, so the pipeline can be run directly. To run it on the original data, place the original files in the same folders and update the paths in config.yaml.

1.4.4.2. From the pipeline_synthetic_data folder (the folder containing main.py), run:

    python3 main.py

On Windows, use "python main.py" if "python3" is not recognized.

The pipeline will:

I.  Load paths from `config.yaml`

II.  Check that the input files contain all variables listed in harmonization_scripts/check/variables.csv. If they do, it prints "All required variables found for '{column_name}'". If any are missing, it stops with an error and writes their names to missing_vars_{column_name}.txt in the main folder.


III. Load and clean raw BPRHS and PROSPECT data

IV.  Apply cleaning and domain-specific transformations

V.  Merge all harmonized domains (SDOH, Health and FFQ)

VI.  Save the final file to:
  `data/output/synthetic_df_hmz_bprhs_prospect_2026.csv`

VII.  Run a validation/quality control check.


Contact

For questions, feedback, or contributions, please contact:

- Rebecca Batorsky  
- Andreia Martinho  
TIAI, Tufts University
