## Dockerfile

Starts from the docker image of htcondor mini which includes all HTCondor componenets as well as the HTCondor RestAPI. I have also included a pre-exec.sh script which gets run at startup and a startup.py script to create the condor config file based on the environment variables given in spin. The supervisord configuration has been updated to include a second REST api which allows for submitting jobs to the condor_q as well as starting worker nodes on cori.

## HTCondor REST

The built in HTCondor REST api is readonly and gives system information on the condor_q and condor_status. More info can be found in the [REST documentation](https://github.com/htcondor/htcondor-restd).

## Startup scripts

The startup scripts are used to set passwords and configuration files if there are not present, as well as change user permissions on some folders for job submissions.

## Submit REST

### Condor submit
The submit endpoint takes a json object with similar parameters found in a condor job description file. Instead of the `queue` keyword accepting a number the count. As an example the folowing json submits 100 jobs which will run the hostname command into the condor_q.

```json
    {
    "executable":"/bin/hostname",
    "error":"$(Cluster).$(Process).err",
    "log":"$(Cluster).$(Process).log",
    "output":"$(Cluster).$(Process).out",
    "request_cpus":"1",
    "request_disk":"1024MB",
    "request_memory":"1024MB", 
    "count": "100"
    }
```
This json document is passed to the rest endpoint as a data parameter. It's important to note that for security the service is availbile on port 8008, which is only accessible inside NERSC networks from spin, and an `Auth` header is equired to run functions. The Auth string can be found by executing a shell in the running spin container.

```bash
curl -H 'Content-Type: application/json' -H 'Auth: xxxxxxxxxxxxxxx' -d '{"error":"$(Cluster).$(Process).err","executable":"/bin/hostname","log":"$(Cluster).$(Process).log","output":"$(Cluster).$(Process).out","request_cpus":"1","request_disk":"1024MB","request_memory":"1024MB", "count": "12000"}' <workload name>-loadbalencer.<namespace>.<cluster>.svc.spin.nersc.org:8008/submit
```

### SUperFacility API REST

The submission system for cori is handled via the SuperFacility API. To start an execute node you can run.

```bash
curl -H 'Content-Type: application/json' -H 'Auth: xxxxxxxxxxxxxxx' centralmanager-loadbalancer.htcondor.production.svc.spin.nersc.org:8008/worker/cori
```