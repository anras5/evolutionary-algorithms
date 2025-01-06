#!/bin/bash

export DIR_WITH_FRAMS_LIBRARY=/Users/filipmarciniak/studia/st2sem2/amib/Framsticks50
cp -f FramsticksEvolutionEA.py ../framspy/FramsticksEvolution.py
cd ../framspy || exit


run_algorithm() {
    iteration="$1"

    start_time=$(date +%s)

    # Uruchomienie algorytmu
    uv run FramsticksEvolution.py \
        -path "$DIR_WITH_FRAMS_LIBRARY" \
        -sim "eval-allcriteria.sim;deterministic.sim;sample-period-2.sim;only-body.sim" \
        -opt vertpos \
        -popsize 200 \
        -generations 150 \
        -hof_size 1 \
        -hof_savefile "lab6/ea/HoF/$iteration.gen" \
        -deap_logfile "lab6/ea/Deap/$iteration.csv" \
        -function reciprocal

    # Wypisanie czasu wykonania algorytmu do times.txt
    end_time=$(date +%s)
    elapsed_time=$((end_time - start_time))
    echo "${iteration},${elapsed_time}" >> "lab6/ea/times.txt"

}

export -f run_algorithm

mkdir -p "lab6/ea/Hof/"
mkdir -p "lab6/ea/Deap/"
rm -f "lab6/ea/times.txt"
echo "N,time" >> "lab6/ea/times.txt"
iterations=(1 2 3 4 5 6 7 8 9 10)
parallel run_algorithm ::: "${iterations[@]}"

echo "----------------------------------------------------------------------"
echo "Finished for ea"