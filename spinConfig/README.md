# Running HTCondor in spin at NERSC

## Docker image
tylern4/condor:nesr

## Ports
5432 -> 5432


## Environment Variables

NAME=tylern
PORT=5432
HOSTNAME=htcondor-loadbalancer.tylern.development.svc.spin.nersc.org
PASSWORDFILE=/etc/condor/passwords.d/spin.password

## Volumes

### Required

### Helpful


## Permissions

Drop ALL



## Load balancer

8080 -> 80