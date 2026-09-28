#!/bin/bash -l
#SBATCH -J rf_hmz
#SBATCH --time=7-00:00:00
#SBATCH -N 1
#SBATCH --cpus-per-task=12
#SBATCH --mem=100Gb
#SBATCH --partition=patralab,largemem,batch,preempt
#SBATCH --exclude=s1cmp006,s1cmp007
#SBATCH --output=rf_%j.out
#SBATCH --error=rf_%j.err

module purge
export SINGULARITY_BIND="/cluster/tufts"

# Expect 9 args:
# 1 nclass
# 2 outvar
# 3 cohort
# 4 seed
# 5 visit
# 6 importance
# 7 data_string
# 8 cross_cohort_val
# 9 regress batch

if [ "$#" -ne 9 ]; then
  echo "ERROR: expected 9 arguments, got $#"
  echo "Usage: sbatch 05_03_sbatch_tune_v2_a1c.sh <nclass> <outvar> <cohort> <seed> <visit> <importance> <data_string> <cross_cohort_val> <regress_batch>"
  exit 1
fi

/cluster/tufts/biocontainers/tools/r-scrnaseq/4.4.0/bin/Rscript --no-save 05_03_rf_v2_a1c.R "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"