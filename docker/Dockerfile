FROM ubuntu:18.04
MAINTAINER funnybrum@gmial.com

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y install cron && \
    apt-get -y install python python-pip && \
    apt-get -y install tzdata

# Cron setup
ADD docker/crontab /etc/cron.d/schedule
RUN chmod 0644 /etc/cron.d/schedule
RUN crontab /etc/cron.d/schedule
RUN touch /var/log/cron.log

# Python scripts
ADD . /site_monitor
RUN rm -rf /site_monitor/venv
RUN pip install -r /site_monitor/requirements.txt

# Set the correct timezone
RUN ln -snf /usr/share/zoneinfo/Europe/Sofia /etc/localtime && echo Europe/Sofia > /etc/timezone

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log
