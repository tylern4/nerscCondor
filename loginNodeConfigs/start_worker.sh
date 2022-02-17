#!/bin/bash

# kill $(ps aux | grep -v grep | grep -i condor_master | awk '{print $2}')

# Where condor is installed (I compiled v9.5 here)
export CONDOR_INSTALL=/global/common/software/m3792/htcondor

# Add condor_* exes/scripts to path
export PATH=$CONDOR_INSTALL/bin:$CONDOR_INSTALL/sbin:$PATH

# Removes any old log files
rm -rf $SCRATCH/condor/$(hostname)

# Create directory for logs
mkdir -p $SCRATCH/condor/$(hostname)/log
# Create directory where jobs are run
mkdir -p $SCRATCH/condor/$(hostname)/execute
# Create directory to store queued jobs
mkdir -p $SCRATCH/condor/$(hostname)/spool
# May not be needed?
mkdir -p $SCRATCH/condor/$(hostname)/log/daemon_sock

# Make sure permissions on new folders are correct
chgrp -R tylern $SCRATCH/condor/$(hostname)
chmod o+rx $SCRATCH/condor/$(hostname)/spool
chmod o+rx $SCRATCH/condor/$(hostname)/log
chmod o+rx $SCRATCH/condor/$(hostname)/execute

# Set the directory where your config files are
# Should have your condor_config.worker.cori files in it
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

# Just make sure we are loading the right config file
echo $CONDOR_CONFIG

# Start the master deamon running
condor_master
