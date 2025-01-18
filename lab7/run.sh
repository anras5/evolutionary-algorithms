#!/bin/bash

export DIR_WITH_FRAMS_LIBRARY=/Users/filipmarciniak/studia/st2sem2/amib/Framsticks50
cp -f FramsticksEvolution.py ../framspy/FramsticksEvolution.py
cd ../framspy || exit

mkdir -p "lab7"

#-initialgenotype "FX[Gpart]rCXmMX[|,r:1,-1:-2.775]" \


uv run FramsticksEvolution.py \
    -path "$DIR_WITH_FRAMS_LIBRARY" \
    -sim "eval-allcriteria.sim;deterministic.sim;sample-period-longest.sim;recording-body-coords.sim" \
    -genformat 1 \
    -popsize 80 -generations 150 -hof_size 1 \
    -hof_savefile "lab7/test_height.gen" \
    -deap_logfile "lab7/test_height.csv"