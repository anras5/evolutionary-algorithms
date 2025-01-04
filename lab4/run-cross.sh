#!/bin/bash

export DIR_WITH_FRAMS_LIBRARY=/Users/filipmarciniak/studia/st2sem2/amib/Framsticks50
cp -f lab_4_cross.py ../framspy/lab_4_cross.py
cd ../framspy || exit

G_values=(0 1 4 9)

run_algorithm() {
    G="$1"

    uv run lab_4_cross.py \
        --path "$DIR_WITH_FRAMS_LIBRARY" \
        --sim "eval-allcriteria.sim;deterministic.sim;sample-period-2.sim;only-body.sim" \
        --iterations 10 \
        --generations 130 \
        --individuals 250 \
        --gen_format "$G"

}

export -f run_algorithm
parallel run_algorithm ::: "${G_values[@]}"
