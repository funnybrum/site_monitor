# !/bin/bash
BASEDIR=$(dirname "$0")
 
cd "$BASEDIR"
if test -f "$FILE"; then
  . ./venv/bin/activate
fi
export PYTHONIOENCODING=utf-8
python launcher.py $@
