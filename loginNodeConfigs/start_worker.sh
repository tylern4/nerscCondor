#!/bin/bash

# kill $(ps aux | grep -v grep | grep -i condor_master | awk '{print $2}')


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

condor_master
