ARG VERSION=9.7-el7
FROM htcondor/mini:$VERSION
ENV VERSION=$VERSION

RUN ln -s /usr/libexec/condor/* /usr/libexec

ENV CONDOR_CONFIG=/data/htcondorlogs/95-NERSC.conf
COPY start.sh /start.sh

