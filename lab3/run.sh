#!/bin/bash

export DIR_WITH_FRAMS_LIBRARY=/Users/filipmarciniak/studia/st2sem2/amib/Framsticks50
cd ../framspy || exit

# oznaczenia różnych plików z prawdopodobieństwem
P_values=(0 1 2 3)


# funkcja uruchamiająca algorytm genetyczny dla danego pliku z prawdopodobieństwem
run_algorithm() {
    iteration="$1"
    P="$2"
    change_mutation="$3"

    start_time=$(date +%s)

    # Uruchomienie algorytmu
    uv run FramsticksEvolution.py \
        -path "$DIR_WITH_FRAMS_LIBRARY" \
        -sim "eval-allcriteria.sim;deterministic.sim;sample-period-longest.sim;wlasne-prawd-$P.sim" \
        -opt velocity -max_numparts 15 -max_numjoints 30 \
        -max_numneurons 20 -max_numconnections 30 \
        -genformat 1 -pxov 0 \
        -popsize 80 -generations 140 -hof_size 1 \
        -hof_savefile "lab3/$P/HoF/$iteration.gen" \
        -deap_logfile "lab3/$P/Deap/$iteration.csv" \
        -change_mutation "$change_mutation"

    # Wypisanie czasu wykonania algorytmu do times.txt
    end_time=$(date +%s)
    elapsed_time=$((end_time - start_time))
    echo "${iteration},${elapsed_time}" >> "lab3/$P/times.txt"

}

export -f run_algorithm

for P in "${P_values[@]}"; do
    mkdir -p "lab3/$P/HoF/"
    mkdir -p "lab3/$P/Deap/"
    rm -f "lab3/$P/times.txt"
    echo "N,time" >> "lab3/$P/times.txt"
    # Uruchomienie algorytmu dla każdej wartości P przy użyciu parallel
    iterations=(1 2 3 4 5 6 7 8 9 10)
    # jeśli P=3 to zmieniamy mutację
    parallel run_algorithm ::: "${iterations[@]}" ::: "$P" ::: "$((P == 3))"

    echo "----------------------------------------------------------------------"
    echo "Finished for $P"
done