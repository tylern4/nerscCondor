#!/bin/bash

/usr/bin/hostname

SLEEP_TIME=$((1 + $RANDOM % 120))

echo $SLEEP_TIME

sleep $SLEEP_TIME

shifter --image=ubuntu:latest cat /etc/os-release
