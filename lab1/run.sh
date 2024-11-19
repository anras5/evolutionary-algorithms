#!/bin/bash

export DIR_WITH_FRAMS_LIBRARY=/Users/filipmarciniak/studia/st2sem2/amib/Framsticks50
cd ../framspy || exit

# Wartości M siły mutacji
M_values=(0 005 010 020 030 040 050)

# funkcja uruchamiająca algorytm genetyczny 10 razy dla danego M
run_algorithm_ten_times() {
    M="$1"
    mkdir -p "lab1/f9-mut-$M/HoF/"
    mkdir -p "lab1/f9-mut-$M/Deap/"
    rm -f "lab1/f9-mut-$M/times.txt"
    echo "N,time" >> "lab1/f9-mut-$M/times.txt"

    for N in {1..10}; do
        # Pomiar czasu wykonania algorytmu
        start_time=$(date +%s)

        # Uruchomienie algorytmu
        uv run FramsticksEvolution.py \
            -path "$DIR_WITH_FRAMS_LIBRARY" \
            -sim "eval-allcriteria.sim;deterministic.sim;sample-period-2.sim;f9-mut-$M.sim" \
            -opt vertpos -max_numparts 30 -max_numgenochars 50 -initialgenotype "/*9*/BLU" \
            -popsize 60 -generations 130 -hof_size 1 \
            -hof_savefile "lab1/f9-mut-$M/HoF/f9-$N.gen" \
            -deap_logfile "lab1/f9-mut-$M/Deap/f9-$N.csv"

        # Wypisanie czasu wykonania algorytmu do times.txt
        end_time=$(date +%s)
        elapsed_time=$((end_time - start_time))
        echo "$N,${elapsed_time}" >> "lab1/f9-mut-$M/times.txt"
    done

}

export -f run_algorithm_ten_times

# Uruchomienie algorytmu dla każdej wartości M przy użyciu parallel
parallel run_algorithm_ten_times ::: "${M_values[@]}"
