ARG VERSION=9.5-el7
FROM htcondor/mini:$VERSION
ENV VERSION=$VERSION

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

COPY --chown=submituser:submituser src /app
RUN chown -R submituser:submituser /app
