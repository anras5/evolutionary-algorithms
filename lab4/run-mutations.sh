#!/bin/bash

export DIR_WITH_FRAMS_LIBRARY=/Users/filipmarciniak/studia/st2sem2/amib/Framsticks50
cp -f lab_4_mutate.py ../framspy/lab_4_mutate.py
cd ../framspy || exit

uv run lab_4_mutate.py \
 --path "$DIR_WITH_FRAMS_LIBRARY" \
 --sim "eval-allcriteria.sim;deterministic.sim;sample-period-2.sim;only-body.sim" \
 --iterations 10 \
 --generations 130
