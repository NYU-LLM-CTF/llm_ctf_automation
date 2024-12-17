#!/bin/bash

JSON_PATH="/home/ms12416/projects/llm_ctf_automation/CSAW24_LLMAC_DB/competition24.json"
CONFIG_PATH="config/base_config.yaml"

jq -r '. | to_entries[] | .key' $JSON_PATH | while read challenge_name; do
  echo "Running challenge: $challenge_name"
  python llm_ctf_solve.py -c $CONFIG_PATH --dataset $JSON_PATH --challenge "$challenge_name"
done