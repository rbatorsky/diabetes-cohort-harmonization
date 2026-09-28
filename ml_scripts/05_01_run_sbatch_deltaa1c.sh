#!/bin/bash

nclass=2
outvar=delta_a1c_v1_v2        
importance=none
data_string=all
visit=a1c_change
regress_batch=0

# -------------------------
# Within-cohort (xcv=0)
# -------------------------
cross_cohort_val=0
for cohort in none; do
  for seed in {1..10}; do
    echo "Running cohort=$cohort nclass=$nclass outvar=$outvar seed=$seed visit=$visit importance=$importance data_string=$data_string xcv=$cross_cohort_val regress_batch=$regress_batch"
    sbatch 05_01_sbatch_tune_deltaa1c.sh $nclass $outvar $cohort $seed $visit $importance $data_string $cross_cohort_val $regress_batch
  done
done

# # -------------------------
# # Cross-cohort (xcv=1..4), cohort must be none
# # -------------------------
# for seed in {1..10}; do
#   for cross_cohort_val in 1 2 3 4; do
#     echo "Running cohort=none nclass=$nclass outvar=$outvar seed=$seed visit=$visit importance=$importance data_string=$data_string xcv=$cross_cohort_val regress_batch=$regress_batch"
#     sbatch 05_sbatch_tune.sh $nclass $outvar none $seed $visit $importance $data_string $cross_cohort_val $regress_batch
#   done
# done