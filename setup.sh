#!/usr/bin/env bash

# Build main docker image
docker build --build-arg HOST_UID=$(id -u) -t ctfenv .

# # Build docker image for each challenge
# for d in LLM_CTF_Database/{rev}/*; do
#     if [ -d "$d" ]; then
#         echo "Building $d"
#         image_name=$(jq -r .container_image < "$d"/challenge.json)
#         is_compose=$(jq -r .compose < "$d"/challenge.json)
#         if [ "$is_compose" = "true" ]; then
#             docker compose -f "$d"/docker-compose.yml build
#         elif [ "$image_name" = "null" ]; then
#             continue
#         else
#             docker build -t "$image_name" "$d"
#         fi
#     fi
# done

networkname="ctfnet"
network_exists=$(docker network ls | grep $networkname)
# Create network
if [ -z "$network_exists" ]; then
    docker network create ctfnet
else
    echo "Network ${networkname} already exists, skip!"
fi

# Download and unpack Ghidra
if [ ! -d ghidra_11.0.1_PUBLIC ]; then
    wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.0.1_build/ghidra_11.0.1_PUBLIC_20240130.zip
    unzip ghidra_11.0.1_PUBLIC_20240130.zip
    rm ghidra_11.0.1_PUBLIC_20240130.zip
fi
