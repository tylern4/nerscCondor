import os

config_template = """# Config created by /root/config/startup.py
MASTER_NAME = {USERNAME}
SCHEDD_NAME = {USERNAME}
CONDOR_HOST = {HOSTNAME}
COLLECTOR_HOST = $(CONDOR_HOST):{PORT}

USE_SHARED_PORT = True
SHARED_PORT_ARGS = -p {PORT}

SHARED_PORT_PORT = {PORT}

UID_DOMAIN = {USERNAME}-condor
DAEMON_LIST = MASTER, COLLECTOR, NEGOTIATOR, SCHEDD

START = True
SUSPEND = False
PREEMPT = False
KILL = False

PRIVATE_NETWORK_NAME = $(FULL_HOSTNAME)
TCP_FORWARDING_HOST = {HOSTNAME}


SEC_PASSWORD_FILE = /etc/condor/passwords.d/{PASSWORDFILE}
SEC_DEFAULT_AUTHENTICATION_METHODS = PASSWORD, FS

ALLOW_READ = 128.55.*, 10.*, $(FULL_HOSTNAME), {HOSTNAME}, *
ALLOW_WRITE = 128.55.*, 10.*, $(FULL_HOSTNAME), {HOSTNAME}, *

ALLOW_ADVERTISE_STARTD = $(ALLOW_WRITE)
ALLOW_ADVERTISE_SCHEDD = $(ALLOW_WRITE)
ALLOW_WRITE_STARTD = $(ALLOW_WRITE)
ALLOW_READ_STARTD = $(ALLOW_WRITE)
ALLOW_WRITE_SCHEDD = $(ALLOW_WRITE)
ALLOW_READ_SCHEDD = $(ALLOW_WRITE)
ALLOW_ADVERTISE_MASTER = $(ALLOW_WRITE)

NEGOTIATOR.ALLOW_READ = $(ALLOW_READ)
NEGOTIATOR.ALLOW_WRITE = $(ALLOW_WRITE)

ALLOW_NEGOTIATOR = *

QUEUE_SUPER_USERS = root, condor, condor_pool, {USERNAME}

NEGOTIATOR_INTERVAL = 5

COLLECTOR_DEBUG = D_FULLDEBUG
NEGOTIATOR_DEBUG = D_FULLDEBUG
MATCH_DEBUG = D_FULLDEBUG
SCHEDD_DEBUG = D_FULLDEBUG

SYSTEM_PERIODIC_HOLD_SUBCODE = MemoryUsage > RequestMemory
SYSTEM_PERIODIC_HOLD = JobRunCount > 100 || MemoryUsage > RequestMemory
"""

perlmutter_conf = """########################################
# Config created by /root/config/startup.py
# Host and port
CONDOR_HOST = {HOSTNAME}:{PORT}
COLLECTOR_HOST = $(CONDOR_HOST)?sock=collector

FILESYSTEM_DOMAIN = $(HOSTNAME)
UID_DOMAIN = $(HOSTNAME)

USE_CCB = True
CCB_ADDRESS = $(CONDOR_HOST)

DAEMON_LIST = MASTER, STARTD, SHARED_PORT

QUEUE_ALL_USERS_TRUSTED = True

START = True
SUSPEND = False
PREEMPT = False
KILL = False

use feature:PartitionableSlot
use feature : GPUs

USE_SHARED_PORT = True

SCRATCH_DIR = $ENV(SCRATCH:/pscratch/sd/{FIRSTLETTER}/{USERNAME})
HOME_DIR = $ENV(HOME:/global/homes/{FIRSTLETTER}/{USERNAME})
LOCAL_DIR = $(SCRATCH_DIR)/condor/$(HOSTNAME)

RELEASE_DIR = /global/common/software/m3792/alvarez/htcondor

SEC_PASSWORD_FILE = $(HOME_DIR)/.condor/spin.password
SEC_DEFAULT_AUTHENTICATION_METHODS = PASSWORD, FS

ALLOW_READ = 128.55.*, 10.*
ALLOW_WRITE = 128.55.*, 10.*

SCHEDD_DEBUG = D_FULLDEBUG
COLLECTOR_DEBUG = D_FULLDEBUG
NEGOTIATOR_DEBUG = D_FULLDEBUG
MATCH_DEBUG = D_FULLDEBUG
SCHEDD_DEBUG = D_FULLDEBUG
STARTER_ALLOW_RUNAS_OWNER = True

# hold jobs that are more than 2x over memory assigned to the slot.
# https://htcondor.org/wiki-archive/pages/HowToLimitMemoryUsage
MEMORY_EXCEEDED = ((MemoryUsage*2 > Memory) =!= TRUE)
PREEMPT = ($(PREEMPT)) || $(MEMORY_EXCEEDED)
WANT_SUSPEND = $(WANT_SUSPEND) && $(MEMORY_EXCEEDED)
WANT_HOLD = $(MEMORY_EXCEEDED)
WANT_HOLD_REASON = ifThenElse( $(MEMORY_EXCEEDED), \
               "high_mem_usage", \
               undefined )

########################################"""


if __name__ == '__main__':
    env_vars = {key: os.environ.get(key)
                for key in ["USERNAME", "PORT", "HOSTNAME", "PASSWORDFILE"]}
    env_vars["FIRSTLETTER"] = env_vars["USERNAME"][0]
    # Prints a file to be copy/pasted into a config file for cori
    print(perlmutter_conf.format(**env_vars))

    with open("/home/submituser/condor/config.d/95-NERSC.conf", 'w') as config:
        config.write(config_template.format(**env_vars))
