# Setting up condor on login node (cori19)

There are two main components needed for the HTCondor cluster the central manager (CM) and the worker nodes.

To start a CM on a login node, in this case cori19, we can run the following commands.

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

We can test the CM is running with the status command.

```bash
condor_status -any

MyType             TargetType         Name

Collector          None               My Pool - cori19-224.nersc.gov@cori19
Scheduler          None               tylern@cori19
DaemonMaster       None               tylern@cori19
Negotiator         None               tylern@cori19
Accounting         none               <none>
```


### Submit out work to the HTCondor queue

There is a basic condor job file [sleep.job](jobs/sleep.job) which runs a bash script [sleep.sh](jobs/sleep.sh) which takes a random time from 1-20 Seconds, sleeps and then runs a command in a shifter container to show how you can use shifter in a condor job.

```bash
cd jobs
condor_submit sleep.job
```

Once the job is submitted we can check the queue with `condor_q`. In this case we've submitted 10 jobs to the queue.

```bash
condor_q

-- Schedd: tylern@cori19 : <128.55.224.49:9618?... @ 02/17/22 10:47:10
OWNER       BATCH_NAME    SUBMITTED   DONE   RUN    IDLE  TOTAL JOB_IDS
condor_pool ID: 7        2/17 10:47      _      _     10     10 7.0-9

Total for query: 10 jobs; 0 completed, 0 removed, 10 idle, 0 running, 0 held, 0 suspended
Total for all users: 10 jobs; 0 completed, 0 removed, 10 idle, 0 running, 0 held, 0 suspended

```

Jobs will wait in this queue until there are workers ready to run the jobs.



### Start a worker node (via salloc) with [start_worker.sh](start_worker.sh)

```bash
salloc -q interactive -C haswell -N 1 --time 01:00:00;

# Start worker is similar to
./start_worker.sh
```

<!-- Not working how I'd like so not adding it at the moment
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
-->

### Checking on workers

```bash
condor_status -any

MyType             TargetType         Name

Machine            Job                slot1@cmem06
Machine            Job                slot1_1@cmem06
Machine            Job                slot1_2@cmem06
Machine            Job                slot1_3@cmem06
Machine            Job                slot1_4@cmem06
Machine            Job                slot1_5@cmem06
Machine            Job                slot1_6@cmem06
Machine            Job                slot1_7@cmem06
Machine            Job                slot1_8@cmem06
Machine            Job                slot1_9@cmem06
Machine            Job                slot1_10@cmem06
Collector          None               My Pool - cori19-224.nersc.gov@cori19
Submitter          None               condor_pool@tylern-condor
Scheduler          None               tylern@cori19
DaemonMaster       None               tylern@cori19
Negotiator         None               tylern@cori19
Accounting         none               <none>
Accounting         none               condor_pool@tylern-condor

```

And check that jobs are running.

```bash
condor_q

-- Schedd: tylern@cori19 : <128.55.224.49:9618?... @ 02/17/22 11:11:36
OWNER       BATCH_NAME    SUBMITTED   DONE   RUN    IDLE  TOTAL JOB_IDS
condor_pool ID: 7        2/17 10:47      _     10      _     10 7.0-9

Total for query: 10 jobs; 0 completed, 0 removed, 0 idle, 10 running, 0 held, 0 suspended
Total for all users: 10 jobs; 0 completed, 0 removed, 0 idle, 10 running, 0 held, 0 suspended
```


### Cleanup CM/cori19

Kills condor master on your central manager node.

`kill $(ps aux | grep -v grep | grep -i condor_master | awk '{print $2}')`