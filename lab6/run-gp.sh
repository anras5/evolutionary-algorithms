#!/bin/bash

source ../.env
cp -f FramsticksEvolutionGP.py ../framspy/FramsticksEvolutionGP.py
cp -f FramsticksEvolutionGPBare.py ../framspy/FramsticksEvolutionGPBare.py
cd ../framspy || exit

GPs=("gp200" "gp500" "gb200" "gb500")



run_algorithm() {
  iteration="$1"
  directory="$2"
  start_time=$(date +%s)

  # if directory starts with gp then run FramsticksEvolutionGP.py
  # if directory starts with gb then run FramsticksEvolutionGPBare.py
  if [[ $directory == gp* ]]; then
    script="FramsticksEvolutionGP.py"
  else
    script="FramsticksEvolutionGPBare.py"
  fi

  uv run $script \
    -path "$DIR_WITH_FRAMS_LIBRARY" \
    -generations 150 \
    -popsize "$3" \
    -opt vertpos \
    -hof_size 1 \
    -hof_savefile "lab6/$directory/HoF/$iteration.gen" \
    -deap_logfile "lab6/$directory/Deap/$iteration.csv"

  end_time=$(date +%s)
  elapsed_time=$((end_time - start_time))
  echo "${iteration},${elapsed_time}" >> "lab6/$directory/times.txt"
}

export -f run_algorithm

# Run the algorithm for "gp200" and "gp500"
for gp in "${GPs[@]}"; do
  echo "----------------------------------------------------------------------"
  echo "Running for $gp"
  mkdir -p "lab6/$gp/HoF/"
  mkdir -p "lab6/$gp/Deap/"
  rm -f "lab6/$gp/times.txt"
  echo "N,time" >> "lab6/$gp/times.txt"
  iterations=(1 2 3 4 5 6 7 8 9 10)
  parallel run_algorithm ::: "${iterations[@]}" ::: "$gp" ::: "${gp:2}"
  echo "----------------------------------------------------------------------"
  echo "Finished for $gp"
done


