#!/bin/bash
source ../BaseStack/bin/setup_run.sh
PYTHONPATH=`pwd`/src:`pwd`/analysis_src:${PYTHONPATH}
export PYTHONPATH
source ssed/bin/activate
