#!/usr/bin/env bash

# Remove the test logs
mkdir -p chaltest_logs
rm -rf chaltest_logs/*

# If * has no matches, return nothing rather than '*'
shopt -s nullglob

echo "Testing challenges..."
echo "Note: log dir is chaltest_logs/, overall results log is chaltest.log" 
for year in 2013 2014 2018 2019 2020 2021 2022 2023; do
    for event in CSAW-Quals CSAW-Finals ; do
        for category_dir in LLM_CTF_Database/${year}/${event}/* ; do
            cat=$(basename "$category_dir")
            for chal in "$category_dir"/*/challenge.json ; do
                chalname=$(basename "$(dirname "$chal")")
                name="${event}-${year} ${chalname} (${cat})"
                log="chaltest_logs/${year}-${event}-${cat}-${chalname}.log"
                python -m llm_ctf.chaltest -w 30 -d "${chal}" &> "$log" && \
                    echo -e "\x1b[32mPASS ${year}-${event}-${cat}-${chalname}\x1b[0m" || \
                    echo -e "\x1b[31mFAIL ${year}-${event}-${cat}-${chalname}\x1b[0m => $log"
            done
        done
    done
done | tee chaltest.log
