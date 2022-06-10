import math
from platform import node
import pandas as pd
import time
from subprocess import Popen, call, PIPE

from typing import Dict
from ast import Try
from asyncio.log import logger
import uuid
import htcondor
import classad
import os
from SuperfacilityAPI import SuperfacilityAPI, SuperfacilityAccessToken
from pathlib import Path


from flask import Flask, request, jsonify, make_response
from logging.config import dictConfig
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask


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
        access_token = SuperfacilityAccessToken(key_path=pem[0])
        sfapi = SuperfacilityAPI(token=access_token.token)

except Exception as e:
    app.logger.error(f"{type(e).__name__} : {e}")
    sfapi = SuperfacilityAPI()


@app.route('/', methods=['GET'])
def read_root():
    return {"classad": classad.__version__,
            "htcondor": htcondor.__version__}


@app.route('/status/<site>', methods=['GET', 'POST'])
def slurm_status(site=None):
    app.logger.info(f"Getting status of {site}")
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

    response = make_response(jsonify(ret), 200)
    response.headers["Content-Type"] = "application/json"
    return response


def cleandict(content):

    if type(content) is dict:
        for key in content.keys():
            c = str(content[key])
            c = c.split(" ")[0]
            c = c.split(";")[0]
            content[key] = c
    else:
        content = {}

    return content


def time_to_seconds(intime):
    # split off days first
    intime = intime.split("-")
    days = int(intime[0]) if len(intime) > 1 else 0

    # split time into HH:MM:SS
    intime = intime[-1].split(":")

    time_bits = {0: 1, 1: 60, 2: 60*60, 3: 60*60*24}
    total = 0
    # Run in reverse becasue we will always
    # have seconds and not always hours
    # 0 -> sec
    # 1 -> min
    # 2 -> hrs.
    # 3 -> days.
    for i, t in enumerate(intime[::-1]):
        total += (time_bits[i]*int(t))

    if days > 0:
        total += (time_bits[3]*int(days))

    # Return total seconds
    return total


@app.route('/worker/<site>', methods=['GET', 'POST'])
def worker(site):
    # Super simple to auth
    # NOTE: Definitly not secure
    if request.headers.get('Auth') != auth:
        return f"Incorect Auth"

    content = cleandict(request.get_json(silent=True))

    if site == 'cori':
        ret = sfapi.post_job(access_token.token,
                             site='cori', script='/global/homes/t/tylern/spin_condor/worker.cori.job', isPath=True)
    elif site == 'perlmutter':
        ret = sfapi.post_job(access_token.token,
                             site=site, script='/global/homes/t/tylern/alvarez_condor/worker.perlmutter.ss11.job', isPath=True)
    else:
        return "Not a Valid Site"
    try:
        return repr(ret['jobid'])
    except Exception as e:
        return repr(e)


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

    submit_result = schedd.submit(
        hostname_job, count=int(count))  # submit the job

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

    ret = sfapi.projects(token=access_token.token)
    try:
        return repr(ret)
    except Exception as e:
        return "Error " + repr(e)


@app.route('/condorq', methods=['GET', 'POST'])
def condorq():
    try:
        condor_q = get_condor_job_queue()
        return condor_q.to_html()
    except Exception as e:
        response = make_response(jsonify({type(e).__name__: repr(e)}), 500)
        return response


def run_sh_command(cmd, live=True, log=None,
                   show_stdout=True):
    """
    Run a command, catch stdout and stderr and exit_code
    :param cmd:
    :param live: live (boolean, default True - don't run the command but pretend we did)
    :param log:
    :param run_time: flag to print elapsed time as log
    :param show_stdout: flag to show stdout or not
    :param timeout_sec: timeout to terminate the specified command
    :return:

    >>> run_sh_command("ls -al", live=False)
    ("Not live: cmd = 'ls -al'", None, 0)
    """
    std_out = None
    std_err = None
    exit_code = None

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)

    try:
        std_out, std_err = p.communicate()
        if type(std_out) is bytes:
            std_out = std_out.decode()
        if type(std_err) is bytes:
            std_err = std_err.decode()
        if show_stdout:
            print(std_out)  # for printing slurm job id
        exit_code = p.returncode
    except:
        return None, None, -1

    if type(std_out) is bytes:
        std_out = std_out.decode()
    if type(std_err) is bytes:
        std_err = std_err.decode()

    return std_out, std_err, exit_code


#
# System vars, dirs, and cmds
#
user_name = "tylern"
condor_root = ".."

wanted_columns = "ClusterId RequestMemory RequestCpus CumulativeRemoteSysCpu CumulativeRemoteUserCpu JobStatus NumRestarts RemoteHost JobStartDate QDate"
condor_q_cmd = f"condor_q -allusers -af {wanted_columns}"
condor_idle_nodes = 'condor_status -const "TotalSlots == 1" -af Machine'


###################### TODO : These should all be created from a configuration file at some point ######################
MIN_POOL = 0
MAX_POOL = 10
MAX_SUBMIT_SIZE = 10

worker_sizes = {
    "regular_cpu": 256,
    "regular_mem": 512,
}

# Extra partition arguments for cori
squeue_args = {}
#squeue_args["cori"] = "--clusters=all -p genepool,genepool_shared,exvivo,exvivo_shared"
# squeue_args["cori"] = "--clusters=all"
squeue_args["perlmutter"] = "--clusters=all"
############### TODO : These should all be created from a configuration file at some point ###############


def get_current_slurm_workers(site: str = "perlmutter", ret_df: bool = False) -> Dict:
    user_status = {}
    squeue_cmd = f'squeue --format="%.18i %D %.24P %.100j %.20u %.10T %S %e %.70R" {squeue_args[site]}'

    _stdout = sfapi.custom_cmd(
        token=access_token.token, cmd=squeue_cmd, site=site)

    try:
        _stdout = _stdout['output']
    except KeyError:
        app.logger.error(
            "No output from squeue, possbily due to maintenance?!")
        return {"regular_pending": 0, "regular_running": 0}

    # Gets jobs from output
    jobs = [job.split() for job in _stdout.split("\n") if len(job.split()) > 3]
    # Get column names from list
    columns = jobs[0]
    num_cols = len(columns)
    # Remove all instances of column names from list of jobs
    jobs = [job for job in jobs if job != columns and len(job) == num_cols]

    # Make dataframe to query with
    df = pd.DataFrame(jobs, columns=columns)
    df["NODES"] = df["NODES"].astype(int)

    # replace time with value and convert times to datetime
    for time_col in ["START_TIME", "END_TIME"]:
        df.loc[df[time_col] == "N/A", time_col] = "2000-01-01T00:00:00"
        df[time_col] = pd.to_datetime(df[time_col])

    df["TIME_LEFT"] = df["END_TIME"] - df["START_TIME"]

    mask_user = df["USER"] == user_name
    mask_pending = df["STATE"] == "PENDING"
    mask_running = df["STATE"] == "RUNNING"

    mask_condor = df["NAME"].str.contains("condor")

    mask_user = mask_user & mask_condor

    app.logger.info(sum(mask_pending))

    # Each of these selects for a certian type of node based on a set of masks
    # Add the number of nodes to get how many are in each catogory
    user_status["regular_pending"] = sum(
        df[mask_user & mask_pending].NODES
    )
    user_status["regular_running"] = sum(
        df[mask_user & mask_running].NODES
    )
    global slurm_running_df
    slurm_running_df = df[mask_user]

    return user_status


def get_condor_job_queue() -> pd.DataFrame:
    # Runs a condor_q autoformat to get the desired columns back
    _stdout, se, ec = run_sh_command(condor_q_cmd, show_stdout=False)
    if ec != 0:
        print(f"ERROR: failed to execute condor_q command: {condor_q_cmd}")
        return None

    # split outputs by rows
    outputs = _stdout.split("\n")

    # Get the column names from configuration
    columns = wanted_columns.split()
    # Split each row into columns
    queued_jobs = [job.split() for job in outputs]
    # Removes columns with no values (Usually the last column)
    queued_jobs = [q for q in queued_jobs if len(q) != 0]

    # Create a dataframe from the split outputs
    df = pd.DataFrame(queued_jobs, columns=columns)
    # Change the type
    df["RequestMemory"] = df["RequestMemory"].astype(int)
    df["JobStatus"] = df["JobStatus"].astype(int)
    df["RequestMemory"] = df["RequestMemory"].astype(float) / 1024
    df["RequestCpus"] = df["RequestCpus"].astype(float)
    df["CumulativeRemoteSysCpu"] = df["CumulativeRemoteSysCpu"].astype(float)
    df["CumulativeRemoteUserCpu"] = df["CumulativeRemoteUserCpu"].astype(float)

    now = int(time.time())
    df["JobStartDate"] = df["JobStartDate"].str.replace('undefined', str(now))
    df["total_running_time"] = now - df["JobStartDate"].astype(int)
    df["cpu_percentage"] = (((df['CumulativeRemoteSysCpu'] + df['CumulativeRemoteUserCpu']
                              ) / df['RequestCpus']) / df['total_running_time']) * 100

    df["total_q_time"] = df["JobStartDate"].astype(
        int) - df["QDate"].astype(int)

    return df


def determine_condor_job_sizes(df: pd.DataFrame):
    df["mem_bin"] = pd.cut(
        df["RequestMemory"],
        bins=[0, worker_sizes["regular_mem"], 10_000_000],
        labels=["regular", "over-mem"],
    )
    df["cpu_bin"] = pd.cut(
        df["RequestCpus"],
        bins=[0, worker_sizes["regular_cpu"], 10_000_000],
        labels=["regular", "over-cpu"],
    )

    condor_q_status = {}
    mask_running_status = df["JobStatus"].astype(int) == 2
    mask_idle_status = df["JobStatus"].astype(int) == 1
    mask_mem_regular = df["mem_bin"].str.contains("regular")
    mask_cpu_regular = df["cpu_bin"].str.contains("regular")

    mask_over = df["cpu_bin"].str.contains(
        "over") | df["mem_bin"].str.contains("over")

    mask_idle_regular = mask_mem_regular & mask_cpu_regular & mask_idle_status

    condor_q_status["idle_regular"] = sum(mask_idle_regular)
    condor_q_status["running_regular"] = sum(
        mask_mem_regular & mask_cpu_regular & mask_running_status
    )

    condor_q_status["hold_and_impossible"] = sum(mask_over)

    condor_q_status["regular_cpu_needed"] = sum(
        df[mask_idle_regular].RequestCpus)
    condor_q_status["regular_mem_needed"] = sum(
        df[mask_idle_regular].RequestMemory)

    return condor_q_status


def need_new_nodes(condor_job_queue: Dict, slurm_workers: Dict, machine: Dict) -> Dict:
    """
    Using the two dictionaries from the condor_q and squeue determine if we need any new workers fpr the machine type.
    """
    workers_needed = 0

    # Determines how many full (or partially full nodes) we need to create
    _cpu = (
        condor_job_queue[f"{machine}_cpu_needed"] /
        worker_sizes[f"{machine}_cpu"]
    )
    _mem = (
        condor_job_queue[f"{machine}_mem_needed"] /
        worker_sizes[f"{machine}_mem"]
    )
    _cpu = math.floor(_cpu)
    _mem = math.floor(_mem)

    workers_needed += max(_cpu, _mem)

    # If full workers_needed is 0 but we have work to be done still get a node
    if workers_needed == 0:
        if condor_job_queue[f"{machine}_cpu_needed"] or condor_job_queue[f"{machine}_mem_needed"]:
            workers_needed = 1

    # Total number running and pending to run (i.e. worker pool)
    current_pool_size = (
        slurm_workers[f"{machine}_pending"]
        + slurm_workers[f"{machine}_running"]
    )

    # If workers_needed is higher than the pool we'll add the diference
    # Else we don't need workers (add 0)
    workers_needed = max(0, workers_needed - current_pool_size)

    # If we have less running than the minimum we always need to add more
    # Either add what we need from queue (workers_needed)
    # Or what we're lacking in the pool (min - worker pool)
    if current_pool_size < MIN_POOL:
        workers_needed = max(MIN_POOL - current_pool_size, workers_needed)

    # Check to make sure we don't go over the max pool size
    if (workers_needed + current_pool_size) > MAX_POOL:
        # Only add up to max pool and no more
        workers_needed = MAX_POOL - current_pool_size

    return workers_needed


def auto_worker(site):
    if site == 'cori':
        ret = sfapi.post_job(token=access_token.token,
                             site='cori', script='/global/homes/t/tylern/spin_condor/worker.cori.job', isPath=True)
    elif site == 'perlmutter':
        ret = sfapi.post_job(token=access_token.token,
                             site=site, script='/global/homes/t/tylern/alvarez_condor/worker.perlmutter.ss11.job', isPath=True)
    else:
        return "Not a Valid Site"
    try:
        return repr(ret['jobid'])
    except Exception as e:
        return repr(e)


workers_needed = {}


@app.route('/needed', methods=['GET', 'POST'])
def rest_workers_needed():
    # Super simple to auth
    # NOTE: Definitly not secure
    if request.headers.get('Auth') != auth:
        app.logger.error(f"No Auth, not checking on getting new jobs")
    else:
        global workers_needed
        workers_needed = run_workers_needed()

    response = make_response(jsonify(workers_needed), 200)
    return response


@app.route('/current', methods=['GET', 'POST'])
def current():
    return job_queue_df.to_html()


def run_workers_needed():
    global job_queue_df
    job_queue_df = get_condor_job_queue()
    condor_job_queue = determine_condor_job_sizes(job_queue_df)
    app.logger.info(condor_job_queue)
    slurm_workers = get_current_slurm_workers("perlmutter")
    app.logger.info(slurm_workers)
    global workers_needed
    workers_needed = {
        "regular": need_new_nodes(condor_job_queue, slurm_workers, "regular"),
    }

    app.logger.info(workers_needed)
    if workers_needed['regular'] > 0:
        jobid = auto_worker('perlmutter')
        app.logger.info(f'Starting job {jobid}')

    return workers_needed


def run_cleanup():
    # Runs a condor_q autoformat to get the desired columns back
    _stdout, se, ec = run_sh_command(condor_idle_nodes, show_stdout=False)
    if ec != 0:
        print(f"ERROR: failed to execute condor_q command: {condor_q_cmd}")
        return None
    nodes = _stdout.split("\n")[:-1]
    app.logger.info(nodes)

    if len(nodes) == 0:
        return None
    try:
        app.logger.info(slurm_running_df.shape)
    except NameError as e:
        app.logger.info('no slurm nodes yet')
        return None

    for node in nodes:
        try:
            job_id = slurm_running_df[slurm_running_df['NODELIST(REASON)'] ==
                                      node].JOBID.iloc[0]
        except IndexError:
            continue

        app.logger.info(f"Removing {node} with JobID {job_id}")
        x = sfapi.delete_job(access_token.token,
                             site='perlmutter', jobid=job_id)
        app.logger.info(x)

    return nodes


sched = BackgroundScheduler(daemon=True)
sched.add_job(run_workers_needed, 'interval', minutes=2)
sched.add_job(run_cleanup, 'interval', minutes=10)
sched.start()
