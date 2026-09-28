#!/bin/bash

nclass=2
importance=none
data_string=all
cross_cohort_val=0
regress_batch=0
outvar=diabetes_change
visit=change


for cohort in 0 1 none; do
  for seed in 1 2 3 4 5 6 7 8 9 10; do
    echo "Running for cohort=$cohort, nclass=$nclass, outvar=$outvar, seed=$seed, visit=$visit, importance=$importance, data_string=$data_string, \
    cross_cohort_val=$cross_cohort_val regress_batch=$regress_batch"
    sbatch 05_02_sbatch_tune_deltadiab.sh $nclass $outvar $cohort $seed $visit $importance $data_string $cross_cohort_val $regress_batch
  done
done


# #cross cohort validation for visit 1
# for cohort in none; do
#   for seed in 1 2 3 4 5 6 7 8 9 10; do
#     for cross_cohort_val in 1 2 3 4; do
#       echo "Running for cohort=$cohort, nclass=$nclass, outvar=$outvar, seed=$seed, visit=$visit, importance=$importance, data_string=$data_string, \
#       cross_cohort_val=$cross_cohort_val regress_batch=$regress_batch"
#       sbatch 05_02_sbatch_tune_deltadiab.sh $nclass $outvar $cohort $seed $visit $importance $data_string $cross_cohort_val $regress_batch
#     done
#   done
# done
