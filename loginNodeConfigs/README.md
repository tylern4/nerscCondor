# Setting up condor on login node (cori19)

### Cori19

```bash
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

# Load the CM config
export CONFIG_DIR=/global/homes/t/tylern/condor/working_02172022
export CONDOR_CONFIG=$CONFIG_DIR/condor_config.cm.cori19

condor_master

```

### Test to make sure CM is running

```bash
condor_status -any

MyType             TargetType         Name

Collector          None               My Pool - cori19-224.nersc.gov@cori19
Scheduler          None               tylern@cori19
DaemonMaster       None               tylern@cori19
Negotiator         None               tylern@cori19
Accounting         none               <none>
```


### Start a worker node (via salloc) with [start_worker.sh](start_worker.sh)

```bash
salloc -q interactive -C haswell -N 1 --time 01:00:00;

# Start worker is similar to
./start_worker.sh
```

### Start a worker node (via slurm) with [slurm_worker_cori.sh](slurm_worker_cori.sh)

```bash
#!/bin/bash
#SBATCH -N 1
#SBATCH -q regular
#SBATCH -C haswell
#SBATCH -A mxxxx
#SBATCH -J htcondor
#SBATCH --time=00:10:00
#SBATCH --output=%x.%j.out
#SBATCH --error=%x.%j.err

# Probably overkill but
# cd to where configs and start_worker.sh are located
cd /global/homes/t/tylern/condor/working_02172022

./start_worker.sh

```