ARG VERSION=9.5-el7
FROM htcondor/mini:$VERSION
ENV VERSION=$VERSION

# Default envs 
ENV USER=docker \
    PORT=5432 \
    HOSTNAME=nersc.org \
    PASSWORDFILE=/etc/condor/password.d/POOL

COPY pre-exec.sh /root/config/pre-exec.sh
COPY startup.py /root/config/startup.py