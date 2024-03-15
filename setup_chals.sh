#!/bin/bash

valid_opts=0

while getopts ":y:e:t:c:" opt; do
    case $opt in
        y)
        year="$OPTARG"
        valid_opts=$((valid_opts + 1))
        ;;
        e)
        event="$OPTARG"
        valid_opts=$((valid_opts + 1))
        ;;
        t)
        category="$OPTARG"
        valid_opts=$((valid_opts + 1))
        ;;
        c)
        chal="$OPTARG"
        valid_opts=$((valid_opts + 1))
        ;;
        ?)
        echo "Invalid option: -$OPTARG" >&2
        echo "Usage: -y {year} -e {event} -t {category} -c {challenge}" >&2
        exit 1
        ;;
    esac
done

if [ $valid_opts -ne 4 ]; then
    echo "All four options must be provided." >&2
    echo "Usage: -y {year} -e {event} -t {category} -c {challenge}" >&2
    exit 1
fi

chal_path="LLM_CTF_Database/$year/$event/$category/$chal"
cd $chal_path || exit
echo "Building $chal"
image_name=$(jq -r .name < challenge.json)
docker build -t "$image_name" "."