#!/usr/bin/env bash

networkname="ctfnet"
network_exists=$(docker network ls | grep $networkname)
# Create network
if [ -z "$network_exists" ]; then
    docker network create ctfnet
else
    echo "Network ${networkname} already exists, skip!"
fi

BASE=$(dirname $0)
# Build main docker image
cd $BASE/docker/multiagent && docker build -t ctfenv:multiagent .

echo "Installing python package"
pip install --editable .
