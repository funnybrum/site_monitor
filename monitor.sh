# !/bin/bash
cd /root/scripts/site_monitor
. ./env/bin/activate
export PYTHONIOENCODING=utf-8
python launcher.py $@
