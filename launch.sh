#!/usr/bin/env bash

# Default values
trials=3 # Number of trials to run
force=0 # Whether to force re-running the solver even if the log exists
rounds=30 # How many conversation rounds to run
backend="openai"
CONFIG_FILE=$1

function cleanup_container {
    docker stop ctfenv_$(id -u) &> /dev/null
    docker wait ctfenv_$(id -u) &> /dev/null
    docker rm ctfenv_$(id -u) &> /dev/null
    while docker container inspect ctfenv_$(id -u) &> /dev/null ; do
        echo "Waiting for ctfenv_$(id -u) to be removed..."
        sleep 1
    done
}

chal_path="LLM_CTF_Database/${year}/${event}/${category}/${chal}"
echo "Start evaluation on ${year}/${event}/${category}/${chal}"
# bash setup_chals.sh -y "${year}" -e "${event}" -t "${category}" -c "${chal}"
safe_model=$(echo "${model}" | tr '/' '_')
for i in $(seq 1 $trials) ; do
    log="logs/${year}/${event}/${category}/${chal}/conversation.${safe_model}.${i}.json"
    if [ -f "${log}" ]; then
        if [ $force -eq 1 ]; then
            echo "Removing existing log file as requested: ${log}"
            rm "${log}"
        else
            printf '[%d/%d] skipping %s attempting challenge /%s/%s/%s/%s; log exists\n' $i $trials "${model}" "${year}" "${event}" "${category}" "${chal}"
            continue
        fi
    fi
    cleanup_container
    printf '[%d/%d] %s attempting challenge /%s/%s/%s/%s\n' $i $trials "${model}" "${year}" "${event}" "${category}" "${chal}"
    python llm_ctf_solve.py -d -M ${model} -m "${rounds}" -L "${log}" "${chal_path}/challenge.json" --backend "${backend}" "$@"
done
