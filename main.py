import os
import sys
import copy  

#------------------------------------------------------------------------------------------------
# Setting work directory
# -----------------------------------------------------------------------------------------------

project_root = os.path.abspath(os.path.dirname(__file__))

#------------------------------------------------------------------------------------------------
# Setting paths
# -----------------------------------------------------------------------------------------------

scripts_path = os.path.join(project_root, 'scripts')
sys.path.insert(0, scripts_path)
sys.path.insert(0, project_root)

#------------------------------------------------------------------------------------------------
# Importing the config and pipeline functions
# -----------------------------------------------------------------------------------------------

from scripts.config import load_config
from scripts.load import run_loading
from scripts.merge import run_merging
from scripts.transform.transform_ffq import transform_ffq
from scripts.transform.transform_sdoh import transform_sdoh 
from scripts.transform.transform_health import transform_health
from scripts.check.check_variables import check_required_variables 
from scripts.validate import run_validation 

def main():
    print("Starting harmonization pipeline...")

    # Load config
    config = load_config()
    print("Config loaded:")
    for key, path in config.items():
        print(f"  {key}: {path}")

    # Run variable presence check
    print("\nChecking variables in raw data required for harmonization...")
    check_required_variables(config)

    # Load raw data
    print("\nLoading data...")
    loaded_data = run_loading(config)

    # Transformations
    print("\nTransforming data...") 
    
    print("\nRunning FFQ transformation...")
    ffq_data = transform_ffq(config)

    print("\nRunning Health transformation...")
    health_data = transform_health(config)
    
    print("\nRunning SDOH transformation...")
    sdoh_data = transform_sdoh(
        config)


    transformed_data = {
    "ffq": ffq_data,
    "sdoh": sdoh_data,
    "health": health_data}

    for domain in [sdoh_data, health_data, ffq_data]:
        for df in domain.values():
            df['studyid'] = df['studyid'].astype(float)

    # Merge and export
    print("\nMerging data and exporting final output...")
    harmonized_data = run_merging(transformed_data)

    # Validation step
    print("\nRunning validation on the harmonized dataset...")
    run_validation(harmonized_data)

    print("\nHarmonization pipeline completed successfully.")

if __name__ == "__main__":
    main()
