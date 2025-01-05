#!/bin/bash

export DIR_WITH_FRAMS_LIBRARY=/Users/filipmarciniak/studia/st2sem2/amib/Framsticks50
cp -f FramsticksEvolution.py ../framspy/FramsticksEvolution.py
cd ../framspy || exit


run_algorithm() {
  iteration="$1"
  start_time=$(date +%s)

  uv run FramsticksEvolution.py \
    -path "$DIR_WITH_FRAMS_LIBRARY" \
    -generations 150 \
    -popsize 200 \
    -opt vertpos \
    -hof_size 1 \
    -hof_savefile "lab6/gp/HoF/$iteration.gen" \
    -deap_logfile "lab6/gp/Deap/$iteration.csv"

  end_time=$(date +%s)
  elapsed_time=$((end_time - start_time))
  echo "${iteration},${elapsed_time}" >> "lab6/gp/times.txt"
}

export -f run_algorithm

mkdir -p "lab6/gp/HoF/"
mkdir -p "lab6/gp/Deap/"
rm -f "lab6/gp/times.txt"
echo "N,time" >> "lab6/gp/times.txt"
iterations=(1 2 3 4 5 6 7 8 9 10)
parallel run_algorithm ::: "${iterations[@]}"

echo "----------------------------------------------------------------------"
echo "Finished for gp"
