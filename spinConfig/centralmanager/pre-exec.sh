#!/bin/bash

# Remove all old configs
rm -rf /etc/condor/config.d/*

# If variable is set and the file does not exist make a new "Random" password
if [[ ! -f "${PASSWORDFILE}" ]]; then
    uuidgen -r | sed 's/-//g' >> ${PASSWORDFILE}
    cat ${PASSWORDFILE}
fi

# Write our new configs from environment
python3 /root/config/startup.py