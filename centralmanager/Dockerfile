ARG VERSION=9.7-el7
FROM htcondor/mini:$VERSION
ENV VERSION=$VERSION

#java-11-openjdk-devel
RUN yum update -y && yum install -y java-11-openjdk-devel vim zsh htop wget  \
    && yum clean all \
    && rm -rf /var/cache/yum

# && wget -O /etc/yum.repos.d/pegasus.repo http://download.pegasus.isi.edu/wms/download/rhel/7/pegasus.repo \
#     && yum install -y pegasus \

ARG CROMWELL_VERSION=78
WORKDIR /cromwell
RUN wget --quiet -O cromwell.jar https://github.com/broadinstitute/cromwell/releases/download/${CROMWELL_VERSION}/cromwell-${CROMWELL_VERSION}.jar 
RUN wget --quiet -O womtool.jar https://github.com/broadinstitute/cromwell/releases/download/${CROMWELL_VERSION}/womtool-${CROMWELL_VERSION}.jar 

COPY --chown=submituser:submituser cromwell.conf /cromwell/
COPY run_cromwell.sh /cromwell/
RUN chown -R submituser:submituser /cromwell


# Default envs 
ENV USERNAME=docker \
    PORT=9618 \
    HOSTNAME=0.0.0.0 \
    PASSWORDFILE=spin.password

COPY pre-exec.sh /root/config/pre-exec.sh
COPY startup.py /root/config/startup.py
COPY submit_rest.sh /usr/local/bin/submit_rest.sh
COPY supervisord.conf /etc/supervisord.conf

COPY src/requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip3 install --upgrade pip && pip3 install setuptools-rust
RUN pip3 install -r requirements.txt
RUN pip3 install git+https://github.com/tylern4/SuperfacilityConnector.git@main

COPY --chown=submituser:submituser src /app
RUN chown -R submituser:submituser /app
