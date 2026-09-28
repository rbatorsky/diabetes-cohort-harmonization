#!/bin/bash
# Imputation sensitivity analysis: V1 diabetes, pooled cohorts, random split,
# 10 seeds x 3 imputation methods. Same seeds => same train/test splits as the published runs.
mkdir -p logs_impute_sens

nclass=2
outvar=diabetes
cohort=none
visit=v1
importance=boruta
data_string=all
cross_cohort_val=0
regress_batch=0

for impute_method in knn median knn_ind; do
  for seed in 1 2 3 4 5 6 7 8 9 10; do
    echo "Submitting impute_method=$impute_method seed=$seed"
    sbatch 05_04_sbatch_impute_sens.sh $nclass $outvar $cohort $seed $visit $importance $data_string $cross_cohort_val $regress_batch $impute_method
  done
done
