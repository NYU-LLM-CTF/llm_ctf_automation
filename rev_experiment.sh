#!/bin/bash

MODEL="$1"

if [ -z "$MODEL" ]
then
    echo "Usage: $0 <model>"
    exit 1
fi

ARGS="-T 3 -m $MODEL"

bash ./llm_solve.sh ${ARGS} -y 2023 -e  CSAW-Quals -t rev -c "baby's first"
# bash ./llm_solve.sh ${ARGS} -y 2023 -e  CSAW-Quals -t rev -c "baby's third"
bash ./llm_solve.sh ${ARGS} -y 2023 -e  CSAW-Quals -t rev -c "rebug 1"
# bash ./llm_solve.sh ${ARGS} -y 2023 -e  CSAW-Quals -t rev -c "rebug 2"
bash ./llm_solve.sh ${ARGS} -y 2023 -e  CSAW-Quals -t rev -c "rox"
# bash ./llm_solve.sh ${ARGS} -y 2023 -e  CSAW-Quals -t rev -c "whataxor"
# bash ./llm_solve.sh ${ARGS} -y 2023 -e CSAW-Finals -t rev -c "cell"
# bash ./llm_solve.sh ${ARGS} -y 2023 -e CSAW-Finals -t rev -c "unVirtualization"

bash ./llm_solve.sh ${ARGS} -y 2022 -e  CSAW-Quals -t rev -c "dockREleakage"
# bash ./llm_solve.sh ${ARGS} -y 2022 -e  CSAW-Quals -t rev -c "game"
# bash ./llm_solve.sh ${ARGS} -y 2022 -e  CSAW-Quals -t rev -c "AnyaGacha"
# bash ./llm_solve.sh ${ARGS} -y 2022 -e  CSAW-Quals -t rev -c "the_big_bang"
# bash ./llm_solve.sh ${ARGS} -y 2022 -e CSAW-Finals -t rev -c "parallel vm"
# bash ./llm_solve.sh ${ARGS} -y 2022 -e CSAW-Finals -t rev -c "roulette"

# RE-ENABLE
# bash ./llm_solve.sh ${ARGS} -y 2018 -e CSAW-Finals -t rev -c "1nsayne"

# bash ./llm_solve.sh ${ARGS} -y 2019 -e  CSAW-Quals -t rev -c "beleaf"
# bash ./llm_solve.sh ${ARGS} -y 2019 -e  CSAW-Quals -t rev -c "call_site"
# bash ./llm_solve.sh ${ARGS} -y 2019 -e CSAW-Finals -t rev -c "wrangly"

# bash ./llm_solve.sh ${ARGS} -y 2020 -e  CSAW-Quals -t rev -c "baby_mult"
# bash ./llm_solve.sh ${ARGS} -y 2020 -e  CSAW-Quals -t rev -c "ezbreezy"
# bash ./llm_solve.sh ${ARGS} -y 2020 -e  CSAW-Quals -t rev -c "Krakme"
# bash ./llm_solve.sh ${ARGS} -y 2020 -e CSAW-Finals -t rev -c "brrr"
# bash ./llm_solve.sh ${ARGS} -y 2020 -e CSAW-Finals -t rev -c "sourcery"

# bash ./llm_solve.sh ${ARGS} -y 2021 -e  CSAW-Quals -t rev -c "checker"
# bash ./llm_solve.sh ${ARGS} -y 2021 -e  CSAW-Quals -t rev -c "ransomware"

# bash ./llm_solve.sh -y 2018 -e CSAW-Finals -t rev -c "bdos"
# bash ./llm_solve.sh -y 2018 -e CSAW-Finals -t rev -c "corewars"
# bash ./llm_solve.sh -y 2018 -e CSAW-Finals -t rev -c "free_as_in_freedom"
# RE-ENABLE

# bash ./llm_solve.sh -y 2019 -e CSAW-Finals -t rev -c "bunny"
# bash ./llm_solve.sh -y 2019 -e CSAW-Finals -t rev -c "mystery_boi"
# bash ./llm_solve.sh -y 2019 -e CSAW-Finals -t rev -c "steady_counting"
# bash ./llm_solve.sh -y 2019 -e CSAW-Finals -t rev -c "zvetouchny"
# bash ./llm_solve.sh -y 2019 -e  CSAW-Quals -t rev -c "gibberish_check"
# bash ./llm_solve.sh -y 2019 -e  CSAW-Quals -t rev -c "halfpike"
# bash ./llm_solve.sh -y 2019 -e  CSAW-Quals -t rev -c "wizkid"

# bash ./llm_solve.sh -y 2020 -e CSAW-Finals -t rev -c "rap"
# bash ./llm_solve.sh -y 2020 -e CSAW-Finals -t rev -c "yeet"
# bash ./llm_solve.sh -y 2020 -e  CSAW-Quals -t rev -c "blox1"
# bash ./llm_solve.sh -y 2020 -e  CSAW-Quals -t rev -c "take-it-easy"
# bash ./llm_solve.sh ${ARGS} -y 2020 -e  CSAW-Quals -t rev -c "not_malware" # Large disassembly

# bash ./llm_solve.sh -y 2021 -e CSAW-Finals -t rev -c "Control-master"
# bash ./llm_solve.sh -y 2021 -e CSAW-Finals -t rev -c "glootie"
# bash ./llm_solve.sh -y 2021 -e CSAW-Finals -t rev -c "maze"
# bash ./llm_solve.sh -y 2021 -e CSAW-Finals -t rev -c "sfc"
# bash ./llm_solve.sh -y 2021 -e  CSAW-Quals -t rev -c "hardskull"
# bash ./llm_solve.sh -y 2021 -e  CSAW-Quals -t rev -c "macomal"
# bash ./llm_solve.sh -y 2021 -e  CSAW-Quals -t rev -c "ncore"
# bash ./llm_solve.sh -y 2021 -e  CSAW-Quals -t rev -c "turning_trees"

# bash ./llm_solve.sh -y 2022 -e CSAW-Finals -t rev -c "babyauth"
# bash ./llm_solve.sh -y 2022 -e CSAW-Finals -t rev -c "Colorblind"

# bash ./llm_solve.sh -y 2023 -e CSAW-Finals -t rev -c "Virtualization"
# bash ./llm_solve.sh ${ARGS} -y 2023 -e CSAW-Finals -t rev -c "coconuts"
# bash ./llm_solve.sh ${ARGS} -y 2023 -e CSAW-Finals -t rev -c "hells_bells"
