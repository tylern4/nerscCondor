#!/bin/bash

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

exec gunicorn app:app --reload --bind 0.0.0.0:8008
