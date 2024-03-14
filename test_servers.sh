#!/usr/bin/env bash

COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_RESET='\033[0m'
# Test each server by starting the server container, then starting the client
# and connecting to it with nc -v.
for d in chals/{pwn,crypto}/*; do
    if [ ! -d "$d" ]; then
        continue
    fi
    image_name=$(jq -r .container_image < "$d"/challenge.json)
    if [ "$image_name" = "null" ]; then
        continue
    fi
    port=$(jq -r .internal_port < "$d"/challenge.json)
    docker run -d --rm --network ctfnet --name "$image_name" "$image_name"
    docker run --rm --network ctfnet ctfenv bash -c "sleep 0.5 ; nc -w 1 -W 1 $image_name $port" &&
        echo -e "\n${COLOR_GREEN}Server $image_name is working${COLOR_RESET}" ||
        echo -e "\n${COLOR_RED}Server $image_name is not working${COLOR_RESET}"
    docker stop "$image_name"
done
