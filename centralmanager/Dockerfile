ARG VERSION=9.7-el7
FROM htcondor/mini:$VERSION
ENV VERSION=$VERSION

WORKDIR /home/submituser/condor

ENV USER=docker \
    HOSTNAME=0.0.0.0 \
    PORT=9816 \
    PASSWORDFILE=spin.password

COPY startup.py /root/config/startup.py
COPY pre-exec.sh /root/config/pre-exec.sh
