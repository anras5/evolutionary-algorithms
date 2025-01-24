#!/bin/bash

export DIR_WITH_FRAMS_LIBRARY=/Users/filipmarciniak/studia/st2sem2/amib/Framsticks51
cp -f FramsticksEvolution.py ../framspy/FramsticksEvolution.py
cd ../framspy || exit

G_VALUES=("0" "1" "4" "H")
if [ -z "$1" ]; then
    echo "Please provide the generation to start from"
    exit 1
fi
export START_GENERATION="$1"

run_algorithm() {
    iteration="$1"
    G="$2"
    start_time=$(date +%s)

    mkdir -p "lab7/f$G/genotypes/$iteration"

    uv run FramsticksEvolution.py \
        -path "$DIR_WITH_FRAMS_LIBRARY" \
        -sim "eval-allcriteria-small.sim;deterministic.sim;sample-period-longest.sim;recording-body-coords.sim" \
        -genformat "$G" \
        -popsize 60 -generations 100 -hof_size 1 \
        -hof_savefile "lab7/f$G/HoF/$iteration.gen" \
        -deap_logfile "lab7/f$G/Deap/$iteration.csv" \
        -genotypes_save_dir "lab7/f$G/genotypes/$iteration" \
        -load_file "lab7/f$G/genotypes/$iteration/$START_GENERATION.gen"

    end_time=$(date +%s)
    elapsed_time=$((end_time - start_time))
    echo "${iteration},${elapsed_time}" >> "lab7/f$G/times$START_GENERATION.txt"
}

export -f run_algorithm


for G in "${G_VALUES[@]}"; do
    mkdir -p "lab7/f$G/HoF/"
    mkdir -p "lab7/f$G/Deap/"
    mkdir -p "lab7/f$G/genotypes/"
    rm -f "lab7/f$G/times$START_GENERATION.txt"
    echo "N,time" >> "lab7/f$G/times$START_GENERATION.txt"
    iterations=(1 2 3 4 5 6 7 8 9 10)
    parallel run_algorithm ::: "${iterations[@]}" ::: "$G"

    echo "----------------------------------------------------------------------"
    echo "Finished for $G"
done
