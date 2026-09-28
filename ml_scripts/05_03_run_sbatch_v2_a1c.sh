#!/bin/bash

nclass=2
importance=none
data_string=all
cross_cohort_val=0
regress_batch=0
outvar=a1c_v2
visit=a1c_change


for cohort in none; do
  for seed in 1 2 3 4 5 6 7 8 9 10; do
    echo "Running for cohort=$cohort, nclass=$nclass, outvar=$outvar, seed=$seed, visit=$visit, importance=$importance, data_string=$data_string, \
    cross_cohort_val=$cross_cohort_val regress_batch=$regress_batch"
    sbatch 05_03_sbatch_tune_v2_a1c.sh $nclass $outvar $cohort $seed $visit $importance $data_string $cross_cohort_val $regress_batch
  done
done

