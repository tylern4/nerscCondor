#!/bin/bash
#SBATCH -N 1
#SBATCH -q regular
#SBATCH -C haswell
#SBATCH -A m3792
#SBATCH -J htcondor
#SBATCH --time=00:01:00
#SBATCH --output=slurmout/%x.%j.out
#SBATCH --error=slurmout/%x.%j.err

cd /global/homes/t/tylern/condor/working_02172022

export CONDOR_INSTALL=/global/common/software/m3792/htcondor

export PATH=$CONDOR_INSTALL/bin:$CONDOR_INSTALL/sbin:$PATH

rm -rf $SCRATCH/condor/$(hostname)

mkdir -p $SCRATCH/condor/$(hostname)/log
mkdir -p $SCRATCH/condor/$(hostname)/execute
mkdir -p $SCRATCH/condor/$(hostname)/spool

mkdir -p $SCRATCH/condor/$(hostname)/log/daemon_sock
chgrp -R tylern $SCRATCH/condor/$(hostname)
chmod o+rx $SCRATCH/condor/$(hostname)/spool
chmod o+rx $SCRATCH/condor/$(hostname)/log

export CONFIG_DIR=/global/homes/t/tylern/condor/working_02172022

case $NERSC_HOST in
"perlmutter")
    : # settings for Perlmutter
    export CONDOR_CONFIG=$CONFIG_DIR/condor_config.worker.pm
    ;;
"cori")
    : # settings for Cori
    export CONDOR_CONFIG=$CONFIG_DIR/condor_config.worker.cori
    ;;
esac

echo $CONDOR_CONFIG

condor_master &
CONDOR_PID=$!
wait $CONDOR_PID

echo $CONDOR_PID

sleep 60
