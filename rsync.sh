# !/bin/bash
rsync -Lavz -e "ssh" --exclude "env" --exclude "database" --progress * pi@192.168.0.200:/home/pi/scripts/admon