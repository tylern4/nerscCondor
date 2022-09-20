#!/usr/bin/env bash -l

# Checks if scratch is valid
#if [[ $SCRATCH == *"UNKNOWN"* ]]; then
#    export LOGDIR=$CFS/nstaff/tylern/htcondorscratch
#else
#    export LOGDIR=$SCRATCH/htcondorscratch
#fi

export LOGDIR=$CFS/nstaff/$USER/htcondorscratch
echo $LOGDIR

mkdir -p $LOGDIR/$(hostname)/log
mkdir -p $LOGDIR/$(hostname)/execute
mkdir -p $LOGDIR/$(hostname)/spool

export CONDOR_INSTALL=/global/common/software/m3792/htcondor
export PATH=${PATH}:${CONDOR_INSTALL}/bin:${CONDOR_INSTALL}/sbin
export CONDOR_CONFIG=/global/homes/t/tylern/htcondor_workflow_scron/condor_server.config
echo $(hostname) > $LOGDIR/currenthost

condor_master

sleep infinity
