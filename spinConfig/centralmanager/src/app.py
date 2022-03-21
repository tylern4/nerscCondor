from ast import Try
from asyncio.log import logger
import htcondor
import classad
import os
from SuperfacilityAPI import SuperfacilityAPI
from pathlib import Path


from flask import Flask, request, jsonify
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] [%(levelname)s] %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

# NOTE: Not a secure way to do this
# For testing purposes only
if os.environ.get("PASSWORDFILE") is not None:
    with open(f'/app/{os.environ.get("PASSWORDFILE")}', 'r') as f:
        auth = f.read().rstrip("\n")
        app.logger.info(f"Auth: {auth}")

else:
    auth = None


def check_file_and_open(file_path: str = "") -> str:
    contents = None
    pth = Path(file_path)
    if pth.is_file():
        with open(pth.absolute()) as f:
            contents = f.read().rstrip('\n')
    return contents


try:
    pem = list(Path('/home/submituser/.superfacility').glob('*.pem'))
    if len(pem) > 0:
        clientid = str(pem[0]).split("/")[-1][:-4]
        private = check_file_and_open(str(pem[0]))
        sfapi = SuperfacilityAPI(clientid, private)
except Exception as e:
    sfapi = SuperfacilityAPI(None, None)


@app.route('/', methods=['GET'])
def read_root():
    return {"classad": classad.__version__,
            "htcondor": htcondor.__version__}


@app.route('/status/<site>', methods=['GET', 'POST'])
def slurm_status(site=None):
    # Super simple to auth
    # NOTE: Definitly not secure
    if request.headers.get('Auth') != auth:
        return f"Incorect Auth"

    if site in ['compute', 'computes']:
        site = 'cori,perlmutter'
    elif site in ['filesystem', 'filesystems']:
        site = 'dna,dtns,global_homes,projectb,global_common,community_filesystem'
    elif site in ['login', 'logins']:
        site = 'cori,perlmutter,jupyter,dtns'

    if site == 'all' or site is None:
        ret = sfapi.status(None)
    else:
        ret = [sfapi.status(site) for site in site.split(",")]

    ret = [oj for oj in ret if oj['description'] != 'Retired']
    return repr(ret)


@app.route('/worker/<site>', methods=['GET', 'POST'])
def worker(site):
    # Super simple to auth
    # NOTE: Definitly not secure
    if request.headers.get('Auth') != auth:
        return f"Incorect Auth"

    script = """#!/bin/bash -l
#SBATCH -N 1
#SBATCH -q debug
#SBATCH -C haswell
#SBATCH -A nstaff
#SBATCH -t 00:10:00
#SBATCH --job-name=condor_worker
#SBATCH --exclusive

#SBATCH -e /global/homes/t/tylern/spin_condor/outputs/%j.err
#SBATCH -o /global/homes/t/tylern/spin_condor/outputs/%j.out


cleanup ()
{
    echo $(date)": got the signal "
    kill $(ps aux | grep -v grep | grep -i condor | awk '{print $2}')
    kill $PID
    exit
}

trap cleanup SIGINT

rm -rf $SCRATCH/condor/$(hostname)

export CONDOR_INSTALL=/global/common/software/m3792/htcondor

export PATH=$CONDOR_INSTALL/bin:$CONDOR_INSTALL/sbin:$PATH

mkdir -p $SCRATCH/condor/$(hostname)/log
mkdir -p $SCRATCH/condor/$(hostname)/execute
mkdir -p $SCRATCH/condor/$(hostname)/spool
mkdir -p $SCRATCH/condor/$(hostname)/log/daemon_sock

export CONDOR_CONFIG=/global/homes/t/tylern/spin_condor/condor_config.glidein.cori

echo $CONDOR_CONFIG

condor_master

sleep 7000
    """
    if site == 'cori':
        ret = sfapi.post_job(site=site, script=script, isPath=False)
    elif site == 'coripath':
        ret = sfapi.post_job(site='cori', script='/global/homes/t/tylern/spin_condor/worker.cori.job', isPath=True)
    else:
        return "Not a Valid Site"
    try:
        return repr(ret['jobid'])
    except Exception as e:
        return repr(e)


@app.route('/token', methods=['GET', 'POST'])
def token():
    return str(sfapi.token)


@app.route('/hostname/<count>', methods=['GET', 'POST'])
def hostname_count(count):
    if request.headers.get('Auth') != auth:
        return f"Incorect Auth"

    hostname_job = htcondor.Submit({
        "executable": "/bin/hostname",  # the program to run on the execute node
        # anything the job prints to standard output will end up in this file
        "output": "/home/submituser/jobs/hostname/outputs/hostname.$(Cluster).$(Process).out",
        # anything the job prints to standard error will end up in this file
        "error": "/home/submituser/jobs/hostname/log/hostname.$(Cluster).$(Process).err",
        # this file will contain a record of what happened to the job
        "log": "/home/submituser/jobs/hostname/log/hostname.$(Cluster).$(Process).log",
        "request_cpus": "1",            # how many CPU cores we want
        "request_memory": "128MB",      # how much memory we want
        "request_disk": "128MB",        # how much disk space we want
    })

    # get the Python representation of the scheduler
    schedd = htcondor.Schedd()

    submit_result = schedd.submit(hostname_job, count=int(count))  # submit the job

    return {"cluster": str(submit_result.cluster()), "count": count}


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.headers.get('Auth') != auth:
        return f"Incorect Auth"

    content = request.get_json(silent=True)
    if content is None:
        return {
            "executable": "/bin/hostname",
            "output": "/home/submituser/jobs/hostname/outputs/$(Cluster).$(Process).out",
            "error": "/home/submituser/jobs/hostname/log/$(Cluster).$(Process).err",
            "log": "/home/submituser/jobs/hostname/log/$(Cluster).$(Process).log",
            "request_cpus": "1",
            "request_memory": "128MB",
            "request_disk": "128MB",
        }

    has_keys = [content.__contains__(key) for key in ["executable",
                                                      "output",
                                                      "error",
                                                      "log",
                                                      "request_cpus",
                                                      "request_memory",
                                                      "request_disk"]]
    if sum(has_keys) != 7:
        return {"cluster": "False"}

    job = htcondor.Submit(content)
    schedd = htcondor.Schedd()
    count = int(content.get("count", 1))
    submit_result = schedd.submit(job, count=count)  # submit the job

    return {"cluster": str(submit_result.cluster()), "submit": str(job)}


@app.route('/projects', methods=['GET', 'POST'])
def projects():
    if request.headers.get('Auth') != auth:
        return f"Incorect Auth"

    ret = sfapi.projects()
    try:
        return repr(ret)
    except Exception as e:
        return "Error " + repr(e)


@app.route('/condorq', methods=['GET', 'POST'])
def condorq():
    queries = []
    coll_query = htcondor.Collector().locateAll(htcondor.DaemonTypes.Schedd)
    for schedd_ad in coll_query:
        schedd_obj = htcondor.Schedd(schedd_ad)
        queries.append(schedd_obj.xquery())
    job_counts = {}
    for query in htcondor.poll(queries):
        schedd_name = query.tag()
        job_counts.setdefault(schedd_name, 0)
        x = query.nextAdsNonBlocking()

    return str(x[0])
