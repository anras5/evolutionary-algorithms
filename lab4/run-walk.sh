#!/bin/bash

source ../.env
cp -f lab_4_walk.py ../framspy/lab_4_walk.py
cd ../framspy || exit

uv run lab_4_walk.py \
 --path "$DIR_WITH_FRAMS_LIBRARY" \
 --sim "eval-allcriteria.sim;deterministic.sim;sample-period-2.sim;only-body.sim" \
 --iterations 10 \
 --generations 130
