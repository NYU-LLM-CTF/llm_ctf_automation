#!/usr/bin/env bash

valid_opts=0

while getopts ":y:e:t:c:m:" opt; do
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
        m)
        model="$OPTARG"
        valid_opts=$((valid_opts + 1))
        ;;
        ?)
        echo "Invalid option: -$OPTARG" >&2
        echo "Usage: -y {year} -e {event} -t {category} -c {challenge} -m model" >&2
        exit 1
        ;;
    esac
done

if [ $valid_opts -ne 5 ]; then
    echo "All four options must be provided." >&2
    echo "Usage: -y {year} -e {event} -t {category} -c {challenge} -m {model}" >&2
    exit 1
fi

function cleanup_container {
    docker stop ctfenv &> /dev/null
    docker wait ctfenv &> /dev/null
    docker rm ctfenv &> /dev/null
    while docker container inspect ctfenv &> /dev/null ; do
        echo "Waiting for ctfenv to be removed..."
        sleep 1
    done
}
chal_path="LLM_CTF_Database/${year}/${event}/${category}/${chal}"
echo "Start evaluation on ${year}/${event}/${category}/${chal}"
epoch=5
# bash setup_chals.sh -y "${year}" -e "${event}" -t "${category}" -c "${chal}"
for i in {1..5}; do
    log="logs/${year}/${event}/${category}/${chal}/conversation.${model}.${i}.json"
    if [ -f "${log}" ]; then
        printf '[%02d/10] skipping %s attempting %s for challenge /%s/%s/%s/%s; log exists\n' $i "${model}" "${year}" "${event}" "${category}" "${chal}"
        continue
    fi
    cleanup_container
    printf '[%02d/5] %s attempting %s for challenge /%s/%s/%s/%s\n' $i "${model}" "${year}" "${event}" "${category}" "${chal}"
    python llm_ctf_solve.py -d -M ${model} -m 30 -L "${log}" "${chal_path}/challenge.json"
done