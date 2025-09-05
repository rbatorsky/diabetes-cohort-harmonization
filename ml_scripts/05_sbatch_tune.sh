#!/bin/bash -l
#SBATCH -J rf_hmz
#SBATCH --time=7-00:00:00 
#SBATCH -N 1
#SBATCH -n 12
#SBATCH --mem=100Gb
#SBATCH --exclude=s1cmp006,s1cmp007
#SBATCH --partition=patralab,largemem,batch
#SBATCH --output=rf_%j.out #saving standard output to file
#SBATCH --error=rf_%j.err #saving standard error to file
 
module purge
export SINGULARITY_BIND="/cluster/tufts"

/cluster/tufts/biocontainers/tools/r-scrnaseq/4.4.0/bin/Rscript --no-save 02_tune_commandargs_case_weight.R $1 $2 $3 $4 $5 $6 $7 $8

