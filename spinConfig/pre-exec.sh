#!/bin/bash

# Remove all old configs
rm -rf /etc/condor/config.d/*

# Write our new configs from environment
python3 /root/config/startup.py