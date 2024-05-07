#!/usr/bin/env bash

set -xeuo pipefail

IMGDIR=/fastdata/csaw_chals/llm_ctf_images

NAME="$1" # e.g. asibench_2019q-cry-fault_box
TARNAME=$(echo "$NAME" | sed 's/asibench_//').tar
YEAR=$(echo "$TARNAME" | cut -d'-' -f1)
mkdir -p "$IMGDIR"/"$YEAR"

docker save "$NAME" -o "$IMGDIR"/"$YEAR"/"$TARNAME"
ln -sf "$IMGDIR"/"$YEAR"/"$TARNAME" .
