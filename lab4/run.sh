#!/bin/bash

source ../.env
cd ../framspy || exit

# Oznaczenia genotypów
G_values=(0 1 4 9)

run_algorithm() {
    iteration="$1"
    G="$2"

    mkdir -p "lab4/f$G/genotypes/$iteration"

    start_time=$(date +%s)

    # Uruchomienie algorytmu
    uv run FramsticksEvolution.py \
        -path "$DIR_WITH_FRAMS_LIBRARY" \
        -sim "eval-allcriteria.sim;deterministic.sim;sample-period-2.sim;only-body.sim" \
        -opt vertpos -max_numparts 30 -genformat "$G" \
        -popsize 50 -generations 130 -hof_size 1 \
        -hof_savefile "lab4/f$G/HoF/$iteration.gen" \
        -deap_logfile "lab4/f$G/Deap/$iteration.csv" \
        -function reciprocal \
        -iteration "$iteration"

    # Wypisanie czasu wykonania algorytmu do times.txt
    end_time=$(date +%s)
    elapsed_time=$((end_time - start_time))
    echo "${iteration},${elapsed_time}" >> "lab4/f$G/times.txt"

}


export -f run_algorithm

for G in "${G_values[@]}"; do
    mkdir -p "lab4/f$G/HoF/"
    mkdir -p "lab4/f$G/Deap/"
    mkdir -p "lab4/f$G/genotypes/"
    rm -f "lab4/f$G/times.txt"
    echo "N,time" >> "lab4/f$G/times.txt"
    # Uruchomienie algorytmu dla każdej wartości G przy użyciu parallel
    iterations=(1 2 3 4 5 6 7 8 9 10)
    parallel run_algorithm ::: "${iterations[@]}" ::: "$G"

    echo "----------------------------------------------------------------------"
    echo "Finished for f$G"
done
