#!/bin/bash

echo "Stopping workers"
kill $(ps aux | grep -v grep | grep -i condor | awk '{print $2}')