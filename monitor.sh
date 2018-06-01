# !/bin/bash
BASEDIR=$(dirname "$0")
 
cd "$BASEDIR"
. ./venv/bin/activate
export PYTHONIOENCODING=utf-8
python launcher.py $@
