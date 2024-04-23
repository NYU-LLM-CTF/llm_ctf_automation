#!/bin/bash

TARGET_DIR="$1"
MODEL="$2"

if [ -z "$TARGET_DIR" ]; then
    echo "Usage: $0 [directory]"
    exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory does not exist."
    exit 1
fi

declare -a dir_list

while IFS= read -r line; do
    dir_list+=("$line")
done < <(find "$TARGET_DIR" -mindepth 4 -maxdepth 4 -type d)

echo "Listing all level 4 subdirectories under $TARGET_DIR:"
for dir in "${dir_list[@]}"; do
    # array=(${dir//\// })
    IFS='/' read -ra array <<< "$dir"
    # 0: database 1: year 2: event 3: category 4: challenge
    if [ "${array[1]}" == ".git" ]; then
        continue
    fi
    echo Solving $dir
    bash ./llm_solve.sh -y ${array[1]} -e ${array[2]} -t ${array[3]} -c "${array[4]}" -m ${MODEL}
    # echo ${array[4]}
done
