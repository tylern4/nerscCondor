#!/bin/bash

rm -rf $SCRATCH/condor/$(hostname)

export CONDOR_INSTALL=/global/common/software/m3792/htcondor
export PATH=$CONDOR_INSTALL/bin:$CONDOR_INSTALL/sbin:$PATH

mkdir -p $SCRATCH/condor/$(hostname)/log
mkdir -p $SCRATCH/condor/$(hostname)/execute
mkdir -p $SCRATCH/condor/$(hostname)/spool


export CONDOR_CONFIG=$HOME/condor_spin/condor_config.glidein.$NERSC_HOST

echo $CONDOR_CONFIG

condor_master

sleep infinity