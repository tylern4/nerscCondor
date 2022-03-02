import os

config_template = """# Config created by /root/config/startup.py
CONDOR_HOST = {CENTRALMANAGER}:{PORT}
COLLECTOR_HOST = $(CONDOR_HOST)?sock=collector

FILESYSTEM_DOMAIN = $(HOSTNAME)
UID_DOMAIN = $(HOSTNAME)

USE_CCB = True
CCB_ADDRESS = $(CONDOR_HOST)

DAEMON_LIST = MASTER, SCHEDD

QUEUE_ALL_USERS_TRUSTED = True

START = True
SUSPEND = False
PREEMPT = False
KILL = False

# Machine resource settings
use feature:PartitionableSlot

USE_SHARED_PORT = True

SEC_PASSWORD_FILE = {PASSWORDFILE}
SEC_DEFAULT_AUTHENTICATION_METHODS = PASSWORD, FS

ALLOW_READ = 128.55.*, 10.*
ALLOW_WRITE = 128.55.*, 10.*
ALLOW_WRITE_SCHEDD = $(ALLOW_WRITE)
ALLOW_READ_SCHEDD = $(ALLOW_WRITE)

SCHEDD_DEBUG = D_FULLDEBUG
COLLECTOR_DEBUG = D_FULLDEBUG
NEGOTIATOR_DEBUG = D_FULLDEBUG
MATCH_DEBUG = D_FULLDEBUG
SCHEDD_DEBUG = D_FULLDEBUG
"""

cori_conf = """########################################
# Config created by /root/config/startup.py
# Host and port
CONDOR_HOST = {CENTRALMANAGER}:{PORT}
COLLECTOR_HOST = $(CONDOR_HOST)?sock=collector

USE_CCB = True
CCB_ADDRESS = $(CONDOR_HOST)
USE_SHARED_PORT = True

FILESYSTEM_DOMAIN = $(HOSTNAME)
UID_DOMAIN = $(HOSTNAME)
QUEUE_ALL_USERS_TRUSTED = True

DAEMON_LIST = MASTER, STARTD


START = True
SUSPEND = False
PREEMPT = False
KILL = False


use feature:PartitionableSlot


LOCAL_DIR = /global/cscratch1/sd/{USERNAME}/condor/$(HOSTNAME)
RELEASE_DIR = /global/common/software/m3792/htcondor

SEC_PASSWORD_FILE = /global/homes/t/{USERNAME}/.condor/{LOCALPASSWORDFILE}
SEC_DEFAULT_AUTHENTICATION_METHODS = PASSWORD, FS

ALLOW_READ = 128.55.*, 10.*
ALLOW_WRITE = 128.55.*, 10.*

SCHEDD_DEBUG = D_FULLDEBUG
COLLECTOR_DEBUG = D_FULLDEBUG
NEGOTIATOR_DEBUG = D_FULLDEBUG
MATCH_DEBUG = D_FULLDEBUG
SCHEDD_DEBUG = D_FULLDEBUG

########################################"""


starting_point = """
CONDOR_HOST = centralmanager-loadbalancer.htcondor.development.svc.spin.nersc.org:5432
COLLECTOR_HOST = $(CONDOR_HOST)?sock=collector

FILESYSTEM_DOMAIN = $(HOSTNAME)
UID_DOMAIN = $(HOSTNAME)

USE_CCB = True
CCB_ADDRESS = $(CONDOR_HOST)

DAEMON_LIST = MASTER, STARTD

QUEUE_ALL_USERS_TRUSTED = True

START = True
SUSPEND = False
PREEMPT = False
KILL = False

# Machine resource settings
use feature:PartitionableSlot

USE_SHARED_PORT = True

LOCAL_DIR = /global/cscratch1/sd/tylern/condor/$(HOSTNAME)
RELEASE_DIR = /global/common/software/m3792/htcondor

SEC_PASSWORD_FILE = /global/homes/t/tylern/condor/cm.password
SEC_DEFAULT_AUTHENTICATION_METHODS = PASSWORD, FS

ALLOW_READ = 128.55.*, 10.*
ALLOW_WRITE = 128.55.*, 10.*

SCHEDD_DEBUG = D_FULLDEBUG
COLLECTOR_DEBUG = D_FULLDEBUG
NEGOTIATOR_DEBUG = D_FULLDEBUG
MATCH_DEBUG = D_FULLDEBUG
SCHEDD_DEBUG = D_FULLDEBUG
"""


if __name__ == '__main__':
    env_vars = {key: os.environ.get(key)
                for key in ["USERNAME", "PORT", "HOSTNAME", "PASSWORDFILE", "CENTRALMANAGER"]}

    env_vars['LOCALPASSWORDFILE'] = env_vars['PASSWORDFILE'].split("/")[-1]

    # Prints a file to be copy/pasted into a config file for cori
    print(cori_conf.format(**env_vars))

    with open("/etc/condor/config.d/95-NERSC.conf", 'w') as config:
        config.write(config_template.format(**env_vars))
