ARG VERSION=9.7-el7
FROM htcondor/mini:$VERSION
ENV VERSION=$VERSION


RUN yum install -y vim zsh htop wget \
    && wget -O /etc/yum.repos.d/pegasus.repo http://download.pegasus.isi.edu/wms/download/rhel/7/pegasus.repo \
    && yum install -y pegasus \
    && yum clean all \
    && rm -rf /var/cache/yum

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
