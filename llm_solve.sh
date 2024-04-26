#!/usr/bin/env bash

valid_opts=0

# Default values
trials=5 # Number of trials to run
force=0 # Whether to force re-running the solver even if the log exists

while getopts ":y:e:t:c:m:T:f" opt; do
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
        T)
        trials="$OPTARG"
        ;;
        f)
        force=1
        ;;
        ?)
        echo "Invalid option: -$OPTARG" >&2
        echo "Usage: -y {year} -e {event} -t {category} -c {challenge} -m model [-T {trials=5}] [-- [llm_solve_args]]" >&2
        exit 1
        ;;
    esac
done

if [ $valid_opts -ne 5 ]; then
    echo "All four options must be provided." >&2
    echo "Usage: -y {year} -e {event} -t {category} -c {challenge} -m {model} [-T {trials=5}] [-- [llm_solve_args]]" >&2
    exit 1
fi

# Pop off everything but the args we want to pass to the solver
shift $(($OPTIND - 1))
echo "Extra args to llm_ctf_solve.py: $*"

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
# bash setup_chals.sh -y "${year}" -e "${event}" -t "${category}" -c "${chal}"
safe_model=$(echo "${model}" | tr '/' '_')
for i in $(seq 1 $trials) ; do
    log="logs/${year}/${event}/${category}/${chal}/conversation.${safe_model}.${i}.json"
    if [ -f "${log}" ]; then
        if [ $force -eq 1 ]; then
            echo "Removing existing log file as requested: ${log}"
            rm "${log}"
        else
            printf '[%d/%d] skipping %s attempting %s for challenge /%s/%s/%s/%s; log exists\n' $i $trials "${model}" "${year}" "${event}" "${category}" "${chal}"
            continue
        fi
    fi
    cleanup_container
    printf '[%d/%d] %s attempting %s for challenge /%s/%s/%s/%s\n' $i $trials "${model}" "${year}" "${event}" "${category}" "${chal}"
    python llm_ctf_solve.py -d -M ${model} -m 30 -L "${log}" "${chal_path}/challenge.json" "$@"
done
