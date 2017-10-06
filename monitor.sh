# !/bin/bash
cd /home/pi/scripts/site_monitor
. ./env/bin/activate
python launcher.py $@
