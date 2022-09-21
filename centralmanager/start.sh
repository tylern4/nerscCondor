#!/bin/bash

mkdir -p /data/htcondorlogs/spin/log
mkdir -p /data/htcondorlogs/spin/spool

condor_master

sleep infinity
