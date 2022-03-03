from crypt import methods
import htcondor
import classad

from flask import Flask, request, jsonify
app = Flask(__name__)


@app.route('/', methods=['GET'])
def read_root():
    return {"classad": classad.__version__,
            "htcondor": htcondor.__version__}


@app.route('/hostname/<count>', methods=['GET', 'POST'])
def hostname_count(count):
    hostname_job = htcondor.Submit({
        "executable": "/bin/hostname",  # the program to run on the execute node
        # anything the job prints to standard output will end up in this file
        "output": "/home/submituser/jobs/hostname/outputs/hostname.$(Cluster).$(Process).out",
        # anything the job prints to standard error will end up in this file
        "error": "/home/submituser/jobs/hostname/outputs/hostname.$(Cluster).$(Process).err",
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
    content = request.get_json(silent=True)
    if content is None:
        return {
            "executable": "",
            "output": "$(Cluster).$(Process).out",
            "error": "$(Cluster).$(Process).err",
            "log": "$(Cluster).$(Process).log",
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
