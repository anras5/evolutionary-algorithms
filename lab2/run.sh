#!/bin/bash

export DIR_WITH_FRAMS_LIBRARY=/Users/filipmarciniak/studia/st2sem2/amib/Framsticks50
cd ../framspy || exit

# Oznaczenia genotypów
G_values=(0 1 4 9)

# Rodzaj poprawienia fitness
R_fitness="$1"
if [ -z "$R_fitness" ]; then
    echo "Usage: $0 <R_fitness>"
    exit 1
fi

# funkcja uruchamiająca algorytm genetyczny dla danego genotypu
run_algorithm() {
    iteration="$1"
    G="$2"

    start_time=$(date +%s)

    # Uruchomienie algorytmu
    uv run FramsticksEvolution.py \
        -path "$DIR_WITH_FRAMS_LIBRARY" \
        -sim "eval-allcriteria.sim;deterministic.sim;sample-period-2.sim;only-body.sim" \
        -opt vertpos -max_numparts 30 -genformat "$G" \
        -popsize 100 -generations 130 -hof_size 1 \
        -hof_savefile "lab2/${R_fitness}/f$G/HoF/$iteration.gen" \
        -deap_logfile "lab2/${R_fitness}/f$G/Deap/$iteration.csv" \
        -function "$R_fitness"

    # Wypisanie czasu wykonania algorytmu do times.txt
    end_time=$(date +%s)
    elapsed_time=$((end_time - start_time))
    echo "${iteration},${elapsed_time}" >> "lab2/${R_fitness}/f$G/times.txt"

}

export -f run_algorithm
export R_fitness

for G in "${G_values[@]}"; do
    mkdir -p "lab2/$R_fitness/f$G/HoF/"
    mkdir -p "lab2/$R_fitness/f$G/Deap/"
    rm -f "lab2/$R_fitness/f$G/times.txt"
    echo "N,time" >> "lab2/$R_fitness/f$G/times.txt"
    # Uruchomienie algorytmu dla każdej wartości G przy użyciu parallel
    iterations=(1 2 3 4 5 6 7 8 9 10)
    parallel run_algorithm ::: "${iterations[@]}" ::: "$G"

    echo "----------------------------------------------------------------------"
    echo "Finished for f$G"
done
