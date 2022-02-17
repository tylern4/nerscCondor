#!/bin/bash
#SBATCH -N 1
#SBATCH -q regular
#SBATCH -C haswell
#SBATCH -A m3792
#SBATCH -J htcondor
#SBATCH --time=00:10:00
#SBATCH --output=slurmout/%x.%j.out
#SBATCH --error=slurmout/%x.%j.err

# Probably overkill but
# cd to where configs and start_worker.sh are located
cd /global/homes/t/tylern/condor/working_02172022

./start_worker.sh
