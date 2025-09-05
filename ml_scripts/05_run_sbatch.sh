#!/bin/bash

# args <- commandArgs(trailingOnly = TRUE)
# nclass = args[1]
# outvar = args[2]
# filter_cohort = args[3]
# downsample = args[4]
# seed = args[5]
# visit = args[6]
# importance = args[7]
# data_string = args[8]

importance=boruta
data_string=all

###Both cohorts in baseline
 for cohort in 0 1 none; do
   for nclass in 2; do
     for outvar in diabetes; do
       for downsample in 0; do
         for seed in 1 2 3 4 5 6 7 8 9 10; do
          for visit in v1 v2;do
           echo "Running for cohort=$cohort, nclass=$nclass, outvar=$outvar, downsample=$downsample, seed=$seed, visit=$visit, importance=$importance, data_string=$data_string"
           sbatch 02_sbatch_tune.sh $nclass $outvar $cohort $downsample $seed $visit $importance $data_string
          done
         done
       done
     done
   done
 done

 ##BPRHS ONLY OVER TIME
 for cohort in 0; do
   for nclass in 2; do
     for outvar in diabetes; do
       for ds in 0; do
         for seed in 123; do
           for year in w3 w4; do
             echo "Running for cohort=$cohort, nclass=$nclass, outvar=$outvar, downsample=$ds, seed=$seed, year=$year"
             sbatch 02_sbatch_tune.sh $nclass $outvar $cohort $ds $seed $year
           done
         done
       done
     done
   done
 done

