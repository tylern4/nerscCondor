#!/usr/bin/env bash

if [[ $SCRATCH == *"UNKNOWN"* ]]; then
    export LOGDIR=$CFS/nstaff/tylern/htcondorscratch
else
    export LOGDIR=$SCRATCH/htcondorscratch
fi

echo $LOGDIR

mkdir -p $LOGDIR/$(hostname)/log
mkdir -p $LOGDIR/$(hostname)/execute
mkdir -p $LOGDIR/$(hostname)/spool



export CONDOR_INSTALL=/global/common/software/m3792/htcondor
export PATH=${PATH}:${CONDOR_INSTALL}/bin:${CONDOR_INSTALL}/sbin

export CONDOR_SERVER=$(cat ${LOGDIR}/currenthost)
export CONDOR_CONFIG=/global/homes/t/tylern/htcondor_workflow_scron/condor_worker.config

condor_master

sleep 86000
