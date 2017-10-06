# !/bin/bash
cd /home/pi/scripts/site_monitor
. ./env/bin/activate
APP_CONFIG=./config/ python ./monitor/launcher.py $@
