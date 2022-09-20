## Scrontab

This is the scrontab that starts up on perlmutter every day at 8am pst.
```
#SCRON -q cron
#SCRON --licenses=cfs
#SCRON -A nstaff
#SCRON -t 24:00:00
#SCRON --job-name=htcondor_workflow_node
#SCRON --chdir=/global/homes/t/tylern/htcondor_workflow_scron
#SCRON -o starterlog.out
#SCRON --open-mode=append
0 15 * * 1-5 /global/homes/t/tylern/nerscCondor/centralmanager/startup_htcondor.sh
```

This will call `startup_htcondor.sh` which creates the config files and starts up the HTCondor centarl manager.

