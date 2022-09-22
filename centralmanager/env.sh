export LOGDIR=${CFS}/nstaff/tylern/htcondorscratch
export PORT=9618
export PASSWORDFILE=${HOME}/.condor/cron.password
export CONDOR_INSTALL=/global/common/software/m3792/htcondor
export PATH=${PATH}:${CONDOR_INSTALL}/bin:${CONDOR_INSTALL}/sbin
export CONDOR_SERVER=$(cat ${LOGDIR}/currenthost)

export CONDOR_CONFIG=${HOME}/nerscCondor/centralmanager/htcondor_worker.conf
