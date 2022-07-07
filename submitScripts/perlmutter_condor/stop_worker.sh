#!/bin/bash

echo "Stopping worker $(hostname)!"
echo $SLURM_HOST
kill $(ps aux | grep -v grep | grep -i condor | awk '{print $2}')
kill $(ps aux | grep -v grep | grep -i pagurus | awk '{print $2}')
