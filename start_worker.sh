#!/bin/bash

rm -rf $SCRATCH/condor/$(hostname)

# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/common/software/python/3.9-anaconda-2021.11/lib
# export CONDOR_INSTALL=/global/cfs/projectdirs/jaws/condor/condor
export CONDOR_INSTALL=/global/common/software/m3792/htcondor

export PATH=$CONDOR_INSTALL/bin:$CONDOR_INSTALL/sbin:$PATH

mkdir -p $SCRATCH/condor/$(hostname)/log
mkdir -p $SCRATCH/condor/$(hostname)/execute
mkdir -p $SCRATCH/condor/$(hostname)/spool

case $NERSC_HOST in
"perlmutter")
    : # settings for Perlmutter
    export CONDOR_CONFIG=$HOME/condor/condor_config.spin_connector.pm
    ;;
"cori")
    : # settings for Cori
    export CONDOR_CONFIG=$HOME/condor/condor_config.spin_connector
    ;;
esac

condor_master
