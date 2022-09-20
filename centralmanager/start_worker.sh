#!/bin/bash

export LOGDIR=/global/cfs/cdirs/nstaff/tylern/htcondorscratch
export CONDOR_SERVER=$(cat ${LOGDIR}/currenthost)
rm -rf ${LOGDIR}/$(hostname)

export CONDOR_INSTALL=/global/common/software/m3792/htcondor
export PATH=$CONDOR_INSTALL/bin:$CONDOR_INSTALL/sbin:$PATH


mkdir -p ${LOGDIR}/$(hostname)/log
mkdir -p ${LOGDIR}/$(hostname)/execute
mkdir -p ${LOGDIR}/$(hostname)/spool


export CONDOR_CONFIG=/global/homes/t/tylern/htcondor_workflow_scron/condor_worker.config

echo $CONDOR_CONFIG

condor_master

sleep infinity
