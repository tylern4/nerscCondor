#!/usr/bin/env bash

#if [[ $SCRATCH == *"UNKNOWN"* ]]; then
#    export LOGDIR=$CFS/nstaff/tylern/htcondorscratch
#else
#    export LOGDIR=$SCRATCH/htcondorscratch
#fi
export LOGDIR=${CFS}/nstaff/tylern/htcondorscratch

export PORT=9618
export PASSWORDFILE=${HOME}/.condor/spin.password
export CONDOR_INSTALL=/global/common/software/m3792/htcondor
export PATH=${PATH}:${CONDOR_INSTALL}/bin:${CONDOR_INSTALL}/sbin
export CONDOR_CONFIG=${HOME}/htcondor_workflow_scron/conf_server.conf

python startup.py

echo $LOGDIR
mkdir -p $LOGDIR/$(hostname)/log
mkdir -p $LOGDIR/$(hostname)/execute
mkdir -p $LOGDIR/$(hostname)/spool
echo $(hostname) > $LOGDIR/currenthost

condor_master

sleep 86300
