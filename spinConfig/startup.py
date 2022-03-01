import os

config_template = """# Config created by /root/config/startup.py
MASTER_NAME = {USER}
SCHEDD_NAME = {USER}
CONDOR_HOST = {HOSTNAME}
COLLECTOR_HOST = $(CONDOR_HOST):{PORT}

USE_SHARED_PORT = True
SHARED_PORT_ARGS = -p {PORT}

SHARED_PORT_PORT = {PORT}

UID_DOMAIN = {USER}-condor
DAEMON_LIST = MASTER, COLLECTOR, NEGOTIATOR, SCHEDD

START = True
SUSPEND = False
PREEMPT = False
KILL = False

# Machine resource settings
NUM_SLOTS = 6

PRIVATE_NETWORK_NAME = $(FULL_HOSTNAME)
TCP_FORWARDING_HOST = $(CONDOR_HOST)


SEC_PASSWORD_FILE = {PASSWORDFILE}
SEC_DEFAULT_AUTHENTICATION_METHODS = PASSWORD, FS

ALLOW_READ = 128.55.*, 10.*
ALLOW_WRITE = 128.55.*, 10.*

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

QUEUE_SUPER_USERS = root, condor, condor_pool, {USER}

COLLECTOR_DEBUG = D_FULLDEBUG
NEGOTIATOR_DEBUG = D_FULLDEBUG
MATCH_DEBUG = D_FULLDEBUG
SCHEDD_DEBUG = D_FULLDEBUG
"""

cori_conf = """########################################
# Config created by /root/config/startup.py
CONDOR_HOST = {HOSTNAME}:{PORT}
COLLECTOR_HOST = $(CONDOR_HOST)?sock=collector

FILESYSTEM_DOMAIN = $(HOSTNAME)
UID_DOMAIN = $(HOSTNAME)

DAEMON_LIST = MASTER, STARTD

QUEUE_ALL_USERS_TRUSTED = True


START = True
SUSPEND = False
PREEMPT = False
KILL = False

NETWORK_INTERFACE = bond0.224


# Machine resource settings
use feature:PartitionableSlot

USE_SHARED_PORT = True

LOCAL_DIR = /global/cscratch1/sd/{USER}/condor/$(HOSTNAME)
RELEASE_DIR = /global/common/software/m3792/htcondor

SEC_PASSWORD_FILE = /global/homes/t/{USER}/.condor/{LOCALPASSWORDFILE}
SEC_DEFAULT_AUTHENTICATION_METHODS = PASSWORD, FS

ALLOW_READ = 128.55.*, 10.*
ALLOW_WRITE = 128.55.*, 10.*

SCHEDD_DEBUG = D_FULLDEBUG
COLLECTOR_DEBUG = D_FULLDEBUG
NEGOTIATOR_DEBUG = D_FULLDEBUG
MATCH_DEBUG = D_FULLDEBUG
SCHEDD_DEBUG = D_FULLDEBUG

########################################"""


if __name__ == '__main__':
    env_vars = {key: os.environ.get(key)
                for key in ["USER", "PORT", "HOSTNAME", "PASSWORDFILE"]}

    env_vars['LOCALPASSWORDFILE'] = env_vars['PASSWORDFILE'].split("/")[-1]

    # Prints a file to be copy/pasted into a config file for cori
    print(cori_conf.format(**env_vars))

    with open("/etc/condor/config.d/95-NERSC.conf", 'w') as config:
        config.write(config_template.format(**env_vars))