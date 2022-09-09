#!/bin/bash

set -e
java -Dconfig.file=/cromwell/cromwell.conf -jar /cromwell/cromwell.jar server