#!/bin/bash

if test -f ../config/secrets.yaml; then
    echo "config/secrets.yaml will be used in the generated Docker image."
else
    echo "config/secrets.yaml is missing. Please, set proper credentials before building the Docker image."
    exit -1
fi

cd ..
docker build -f ./docker/Dockerfile . -t site_monitor
cd docker
