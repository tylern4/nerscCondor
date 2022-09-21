#!/bin/bash

# Remove all old configs
rm -rf /etc/condor/config.d/*

python3 /root/config/startup.py
