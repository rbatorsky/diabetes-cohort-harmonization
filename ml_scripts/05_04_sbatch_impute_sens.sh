#!/bin/bash -l
#SBATCH -J rf_impsens
#SBATCH --time=2-00:00:00
#SBATCH -N 1
#SBATCH --cpus-per-task=12
#SBATCH --mem=64Gb
#SBATCH --partition=patralab,batch,preempt
#SBATCH --output=logs_impute_sens/rf_impsens_%j.out
#SBATCH --error=logs_impute_sens/rf_impsens_%j.err

module purge
export SINGULARITY_BIND="/cluster/tufts"

# Expect 10 args:
# 1 nclass
# 2 outvar
# 3 cohort
# 4 seed
# 5 visit
# 6 importance
# 7 data_string
# 8 cross_cohort_val
# 9 regress batch
# 10 impute_method (knn | median | knn_ind)

if [ "$#" -ne 10 ]; then
  echo "ERROR: expected 10 arguments, got $#"
  echo "Usage: sbatch 05_04_sbatch_impute_sens.sh <nclass> <outvar> <cohort> <seed> <visit> <importance> <data_string> <cross_cohort_val> <regress_batch> <impute_method>"
  exit 1
fi

/cluster/tufts/biocontainers/tools/r-scrnaseq/4.4.0/bin/Rscript --no-save 05_04_rf_impute_sens.R "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}"