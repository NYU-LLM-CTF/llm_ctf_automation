#!/bin/bash
array=()
while IFS='' read -r line; do
    array+=("$line")
done < <(docker images --format "{{.Repository}}:{{.Tag}}" | grep "^asibench_")

for item in "${array[@]}"; do
    result=${item#asibench_}
    result=${result%:latest}
    result=${result%/*}
    echo "Exporting $result"
    docker save "$item" -o "/data/ctf_images/validated_oci/$result.tar"
done