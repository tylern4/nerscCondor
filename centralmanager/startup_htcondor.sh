#!/usr/bin/env bash

#if [[ $SCRATCH == *"UNKNOWN"* ]]; then
#    export LOGDIR=$CFS/nstaff/tylern/htcondorscratch
#else
#    export LOGDIR=$SCRATCH/htcondorscratch
#fi
export LOGDIR=${CFS}/nstaff/tylern/htcondorscratch
export CONDOR_PORT=9876
export PASSWORDFILE=${HOME}/.condor/cron.password
export CONDOR_INSTALL=/global/common/software/m3792/htcondor-9.11.2
export PATH=${PATH}:${CONDOR_INSTALL}/bin:${CONDOR_INSTALL}/sbin
export CONDOR_SERVER=$(hostname)

export CONDOR_CONFIG=${HOME}/nerscCondor/centralmanager/htcondor_server.conf

echo $LOGDIR
mkdir -p $LOGDIR/$(hostname)/log
mkdir -p $LOGDIR/$(hostname)/execute
mkdir -p $LOGDIR/$(hostname)/spool
echo $(hostname) > $LOGDIR/currenthost

condor_master

sleep 86300
