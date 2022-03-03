# Running HTCondor in spin at NERSC

## Docker image
Strat by building the central manager image from the [Dockerfile](centralmanager/Dockerfile), this includes a very basic flask app template for sumbmitting work to a rest api.

## Ports
Setup the ports needed for comunicating with htcondor and the submit rest server. You can omit the submit rest server port if you are not planning to use it for submissions. You can also change the `Publish the container port` for htcondor to any other port open to non-http services on spin, just make sure to also include the change in your environment variable configurations.


| Port Name | Publish the container port | Protocol | As a | On listening port |
| --------- | -------------------------- | -------- | ---- | ----------------- |
| htcondor  | 5432                   | TCP      | Layer-4 Load Balencer | 5432 |
| submit    | 8008                   | TCP      | Layer-4 Load Balencer | 8008 |


## Environment Variables

These evironment varibles will be used to create the configuration files for htcondor on startup. It also prints a configuration to the logs to be used when setting up a machine on cori. Replace the values with 

```
USERNAME=nerscuser
PORT=5432
PASSWORDFILE=spin.password
HOSTNAME=<workload name>-loadbalencer.<namespace>.<cluster>.svc.spin.nersc.org
```

## Volumes

There are a few nfs-client volumes to add to the spin configuration in order to make data persistant between restarts.

### Required

Setup a password file for the condor pool, following the instructions in the spinup workshop:

1. Create a secret
Select Resources > Secrets and click Add Secrets.
Select: Available to a single namespace
Select the namespace in the drop down

2. Set Values
```
Name: <name your file>
Key: <Same as your PASSWORDFILE environment>
Value: <make-something-up>
```
3. Click Save

Add to
1. Click on Resources > Workloads, open the ( ⋮ ) menu to the
right of your workload, and select Edit.
2. Expand Volumes; click Add Volumes; select Use a Secret.
3. From the Secret drop-down, choose your file name.
4. Check Select Specific Keys; from the Key drop-down, choose
password. Under Path, enter password.
5. Set Mount Point to /etc/condor/passwords.d.
6. Click Save. 

### Helpful

To save the htcondor queue and cluster numbering between restarts: `/var/lib/condor/spool`

To save a space for your common htcondor submit files and job logs: `/home/submituser/jobs`


## Permissions
Drop:
```
ALL
```

Add:
```
CHOWN
DAC_OVERRIDE
FOWNER
SETGID
SETUID
```


## Load balancer
To view the htcondor read-only rest api you can add a load balancer to point to `8080`

1. Start in Resources > Workload
2. Click Load Balancing, then Add Ingress
3. Set these values
Name: lb
Namespace: <Namespace from previous exercise>
4. Click Specify Hostname to use and add lb.<namespace>.development.svc.spin.nersc.org
5. Scroll down to Target Backend (The Workload type is selected by default) & add these values
Path: Leave blank
Target: app
Port: 8080
6. Click Save