#!/bin/sh

echo "Starting worker on $(hostname)!"

rm -rf $SCRATCH/condor/$(hostname)

export CONDOR_INSTALL=/global/common/software/m3792/alvarez/htcondor
export PATH=$CONDOR_INSTALL/bin:$CONDOR_INSTALL/sbin:$PATH

mkdir -p $SCRATCH/condor/$(hostname)/log
mkdir -p $SCRATCH/condor/$(hostname)/execute
mkdir -p $SCRATCH/condor/$(hostname)/spool

chmod -R 777 $SCRATCH/condor/$(hostname)/execute
chmod -R a+w $SCRATCH/condor/$(hostname)/execute

export CONDOR_CONFIG=$HOME/alvarez_condor/condor_config.glidein.$NERSC_HOST

echo $CONDOR_CONFIG
module load python

/global/cfs/projectdirs/m3792/tylern/local/bin/pagurus \
--move \
--user $USER \
--path $SCRATCH/condor/performance \
--outfile condor_$(hostname)_$SLURM_JOB_ID.csv &

condor_master

# Sleep 3 days
sleep 259200
