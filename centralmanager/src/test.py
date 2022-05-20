import time
import htcondor
import pandas as pd
from subprocess import Popen, call, PIPE


from typing import Dict
from pathlib import Path
from SuperfacilityAPI import SuperfacilityAPI, SuperfacilityAccessToken

try:
    pem = list(Path('/home/submituser/.superfacility').glob('*.pem'))
    if len(pem) > 0:
        access_token = SuperfacilityAccessToken(key_path=pem[0])
        sfapi = SuperfacilityAPI(token=access_token.token)

except Exception as e:
    print(f"{type(e).__name__} : {e}")
    sfapi = SuperfacilityAPI()


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
accnt_name = "jaws_jtm"
# condor_root = "/global/cfs/cdirs/jaws/condor"
condor_root = ".."

normal_worker_q = f"{condor_root}/condor_worker_normal.job"
highmem_worker_jgishared_q = f"{condor_root}/condor_worker_highmem_jgi_shared.job"
highmem_worker_jgilarge_q = f"{condor_root}/condor_worker_highmem_jgi_large.job"
wanted_columns = "ClusterId RequestMemory RequestCpus JobStatus NumRestarts QDate"
condor_q_cmd = f"condor_q -af {wanted_columns}"


###################### TODO : These should all be created from a configuration file at some point ######################
MIN_POOL = 3
MAX_POOL = 100

worker_sizes = {
    "regular_cpu": 64,
    "regular_mem": 128,
    "large_cpu": 72,
    "large_mem": 1450,
    "perlmutter_cpu": 256,
    "perlmutter_mem": 512,
}

default_form = {}
default_form["regular"] = {
    "site": "cori",
    "qos": "genepool_special",
    "constraint": "haswell",
    "account": "fungalp",
    "time": "06:00:00",
    "cluster": "cori",
    "script_location": ".",
}
default_form["large"] = {
    "site": "cori",
    "qos": "exvivo",
    "constraint": "skylake",
    "account": "fungalp",
    "time": "06:00:00",
    "cluster": "escori",
    "script_location": ".",
}

# Extra partition arguments for cori
squeue_args = {}
squeue_args["cori"] = "--clusters=all -p genepool,genepool_shared,exvivo,exvivo_shared"
squeue_args["jgi"] = "-p lr3"
squeue_args["tahoma"] = ""
############### TODO : These should all be created from a configuration file at some point ###############


def get_current_slurm_workers(site: str = "cori") -> Dict:
    squeue_cmd = f'squeue --format="%.18i %D %.24P %.100j %.20u %.10T %S %e" {squeue_args[site]}'
    _stdout = sfapi.custom_cmd(cmd=squeue_cmd)
    _stdout = _stdout['output']

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
    jaws_jtm_status = {}

    mask_jtm = df["USER"] == "jaws_jtm"
    mask_genepool = df["PARTITION"].str.contains("genepool")
    mask_pending = df["STATE"] == "PENDING"
    mask_condor = df["NAME"].str.contains("condor")

    mask_jtm = mask_jtm & mask_condor

    # Each of these selects for a certian type of node based on a set of masks
    # Add the number of nodes to get how many are in each catogory
    jaws_jtm_status["jaws_regular_pending"] = sum(
        df[mask_jtm & mask_pending & mask_genepool].NODES
    )
    jaws_jtm_status["jaws_regular_running"] = sum(
        df[mask_jtm & ~mask_pending & mask_genepool].NODES
    )

    jaws_jtm_status["jaws_large_pending"] = sum(
        df[mask_jtm & mask_pending & ~mask_genepool].NODES
    )
    jaws_jtm_status["jaws_large_running"] = sum(
        df[mask_jtm & ~mask_pending & ~mask_genepool].NODES
    )

    jaws_jtm_status["other_genepool_pending"] = sum(
        df[~mask_jtm & mask_pending & mask_genepool].NODES
    )
    jaws_jtm_status["other_genepool_running"] = sum(
        df[~mask_jtm & ~mask_pending & mask_genepool].NODES
    )

    jaws_jtm_status["other_large_pending"] = sum(
        df[~mask_jtm & mask_pending & ~mask_genepool].NODES
    )
    jaws_jtm_status["other_large_running"] = sum(
        df[~mask_jtm & ~mask_pending & ~mask_genepool].NODES
    )

    return jaws_jtm_status


def get_condor_job_queue() -> pd.DataFrame:
    _stdout, se, ec = run_sh_command(condor_q_cmd, show_stdout=False)
    if ec != 0:
        print(f"ERROR: failed to execute condor_q command: {condor_q_cmd}")
        exit(1)

    # split outputs into
    outputs = _stdout.split("\n")
    columns = wanted_columns.split()

    queued_jobs = [job.split() for job in outputs]
    queued_jobs = [q for q in queued_jobs if len(q) != 0]
    df = pd.DataFrame(queued_jobs, columns=columns)
    df["RequestMemory"] = df["RequestMemory"].astype(int)/1024
    df["JobStatus"] = df["JobStatus"].astype(int)
    df["RequestMemory"] = df["RequestMemory"].astype(float)
    df["RequestCpus"] = df["RequestCpus"].astype(float)
    df["total_q_time"] = int(time.time()) - df["QDate"].astype(int)

    return df


def determine_condor_job_sizes(df: pd.DataFrame):

    df["mem_bin"] = pd.cut(
        df["RequestMemory"],
        bins=[0, worker_sizes["regular_mem"],
              worker_sizes["large_mem"], 10_000_000],
        labels=["regular", "large", "over-mem"],
    )
    df["cpu_bin"] = pd.cut(
        df["RequestCpus"],
        bins=[0, worker_sizes["regular_cpu"],
              worker_sizes["large_cpu"], 10_000_000],
        labels=["regular", "large", "over-cpu"],
    )

    condor_q_status = {}
    mask_running_status = df["JobStatus"].astype(int) == 2
    mask_idle_status = df["JobStatus"].astype(int) == 1
    mask_mem_regular = df["mem_bin"].str.contains("regular")
    mask_mem_large = df["mem_bin"].str.contains("large")
    mask_cpu_regular = df["cpu_bin"].str.contains("regular")
    mask_cpu_large = df["cpu_bin"].str.contains("large")

    mask_over = df["cpu_bin"].str.contains(
        "over") | df["mem_bin"].str.contains("over")

    mask_idle_regular = mask_mem_regular & mask_cpu_regular & mask_idle_status
    mask_idle_large = (mask_mem_large | mask_cpu_large) & mask_idle_status

    condor_q_status["idle_regular"] = sum(mask_idle_regular)
    condor_q_status["running_regular"] = sum(
        mask_mem_regular & mask_cpu_regular & mask_running_status
    )
    condor_q_status["idle_large"] = sum(mask_idle_large)
    condor_q_status["running_large"] = sum(
        (mask_mem_large | mask_cpu_large) & mask_running_status
    )
    condor_q_status["hold_and_impossible"] = sum(mask_over)

    condor_q_status["regular_cpu_needed"] = sum(
        df[mask_idle_regular].RequestCpus)
    condor_q_status["regular_mem_needed"] = sum(
        df[mask_idle_regular].RequestMemory)

    condor_q_status["large_cpu_needed"] = sum(df[mask_idle_large].RequestCpus)
    condor_q_status["large_mem_needed"] = sum(
        df[mask_idle_large].RequestMemory)

    return condor_q_status


def need_new_nodes(condor_job_queue: Dict, slurm_workers: Dict, machine: Dict) -> Dict:
    workers_needed = 0

    # If we need more than a node add a node (or more)
    if (
        condor_job_queue[f"{machine}_cpu_needed"] > worker_sizes[f"{machine}_cpu"]
        or condor_job_queue[f"{machine}_mem_needed"] > worker_sizes[f"{machine}_mem"]
    ):
        # Calculate what we need
        _cpu = (
            condor_job_queue[f"{machine}_cpu_needed"] // worker_sizes[f"{machine}_cpu"]
        )
        _mem = (
            condor_job_queue[f"{machine}_mem_needed"] // worker_sizes[f"{machine}_mem"]
        )
        workers_needed += max(_cpu, _mem)

    # Total number running and pending to run (i.e. worker pool)
    current_pool_size = (
        slurm_workers[f"jaws_{machine}_pending"]
        + slurm_workers[f"jaws_{machine}_running"]
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


def get_condor_job_queue2():
    schedd = htcondor.Schedd()

    queued_jobs = schedd.query()
    df = pd.DataFrame(queued_jobs)
    return print(queued_jobs[0])


if __name__ == '__main__':
    condor_q = get_condor_job_queue()
    print(determine_condor_job_sizes(condor_q))
    # print(get_condor_job_queue2())
