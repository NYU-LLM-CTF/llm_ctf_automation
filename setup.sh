#!/usr/bin/env bash

# Build main docker image
docker build -t ctfenv .

# Build docker image for each challenge
for d in chals/{pwn,crypto,web,misc}/*; do
    if [ -d "$d" ]; then
        echo "Building $d"
        image_name=$(jq -r .container_image < "$d"/challenge.json)
        is_compose=$(jq -r .compose < "$d"/challenge.json)
        if [ "$is_compose" = "true" ]; then
            docker compose -f "$d"/docker-compose.yml build
        elif [ "$image_name" = "null" ]; then
            continue
        else
            docker build -t "$image_name" "$d"
        fi
    fi
done

# Create network
docker network create ctfnet

# Download and unpack Ghidra
if [ ! -d ghidra_11.0_PUBLIC ]; then
    wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.0_build/ghidra_11.0_PUBLIC_20231222.zip
    unzip ghidra_11.0_PUBLIC_20231222.zip
    rm ghidra_11.0_PUBLIC_20231222.zip
fi
