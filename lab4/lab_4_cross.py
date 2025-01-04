import argparse
from dataclasses import dataclass

import pandas as pd
from tqdm import tqdm

from FramsticksLib import FramsticksLib

FITNESS_VALUE_INFEASIBLE_SOLUTION = -999999.0


@dataclass
class Individual:
    genotype: str
    fitness: float

    def __str__(self):
        return f"Genotype: {self.genotype}, Fitness: {self.fitness}"


def frams_crossover(frams_lib, individual_1, individual_2):
    child = frams_lib.crossOver(individual_1, individual_2)
    return child


def genotype_within_constraint(
        genotype, dict_criteria_values, criterion_name, constraint_value
):
    REPORT_CONSTRAINT_VIOLATIONS = False
    if constraint_value is not None:
        actual_value = dict_criteria_values[criterion_name]
        if actual_value > constraint_value:
            if REPORT_CONSTRAINT_VIOLATIONS:
                print(
                    'Genotype "%s" assigned a special ("infeasible solution") fitness because it violates constraint "%s": %s exceeds the threshold of %s'
                    % (genotype, criterion_name, actual_value, constraint_value)
                )
            return False
    return True


def frams_evaluate(frams_lib, individual):
    genotype = individual[0]
    data = frams_lib.evaluate([genotype])
    # print("Evaluated '%s'" % genotype, 'evaluation is:', data)
    valid = True
    try:
        first_genotype_data = data[0]
        evaluation_data = first_genotype_data["evaluations"]
        default_evaluation_data = evaluation_data[""]
        fitness = default_evaluation_data["vertpos"]

    except (KeyError, TypeError) as e:
        valid = False
        # print(
        #     f'Problem "%s" so could not evaluate genotype "%s", hence assigned it a special ("infeasible solution") fitness value: %s'
        #     % (str(e), genotype, FITNESS_VALUE_INFEASIBLE_SOLUTION)
        # )
    if valid:
        default_evaluation_data["numgenocharacters"] = len(genotype)  # for consistent constraint checking below
        valid &= genotype_within_constraint(genotype, default_evaluation_data, "numparts", 30)
    if not valid:
        fitness = FITNESS_VALUE_INFEASIBLE_SOLUTION

    return fitness


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Path to Framsticks library without trailing slash.",
    )
    parser.add_argument(
        "--lib",
        required=False,
    )
    parser.add_argument(
        "--sim",
        required=False,
        default="eval-allcriteria.sim",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        required=False,
        default=10,
        help="Number of iterations from the main evolution (ran with run.sh)."
    )
    parser.add_argument(
        "--generations",
        type=int,
        required=False,
        default=130,
        help="Number of generations in each iteration from the main evolution (ran with run.sh)."
    )
    parser.add_argument(
        "--individuals",
        type=int,
        required=False,
        default=200,
        help="Number of individuals to select from the main evolution (ran with run.sh)."
    )
    parser.add_argument(
        "--gen_format",
        required=True,
        choices=["0", "1", "4", "9"],
        help="Genetic format for genotypes (0, 1, 4, 9).",
    )
    args = parser.parse_args()
    FramsticksLib.DETERMINISTIC = False
    framsLib = FramsticksLib(args.path, frams_lib_name=args.lib, sim_settings_files=args.sim)

    # iterate over saved individuals and save them
    individuals = []
    for iteration in range(1, args.iterations + 1):
        for generation in range(1, args.generations + 1):
            with open(f"lab4/f{args.gen_format}/genotypes/{iteration}/{generation}.gen", "r") as f:
                ind = None
                genotype_line = False
                for line in f:
                    # start of a new individual
                    if line.startswith("org:"):
                        ind = Individual("", -1)

                    # start of genotype
                    if line.startswith("genotype:"):
                        genotype = line.split(":")[1].strip()
                        # ~ starts multiline genotype for f0
                        if genotype == "~":
                            genotype_line = True
                            continue
                        else:
                            ind.genotype = line.split(":")[1].strip()
                    if genotype_line and line.strip() == "~":
                        genotype_line = False
                    if genotype_line:
                        ind.genotype += line

                    # start of fitness values
                    if line.startswith("vertpos:"):
                        vertpos = float(line.split(":")[1].strip())
                        if vertpos > 0:
                            ind.fitness = vertpos

                    # end of individual
                    if line == "\n":
                        # check if vertpos is greater than 0 and if ind is not in the individuals list based on the genotype (to avoid duplicates)
                        if ind.fitness > 0 and ind.genotype not in [i.genotype for i in individuals]:
                            individuals.append(ind)

    # get min and max fitness
    min_fitness = min([i.fitness for i in individuals])
    max_fitness = max([i.fitness for i in individuals])

    # divide the (min, max) range into 200 equal parts
    fitness_range = [min_fitness + (max_fitness - min_fitness) / args.individuals * i for i in range(args.individuals + 1)]
    # save one individual for each of the 200 parts
    selected_individuals = []
    sorted_individuals = sorted(individuals, key=lambda x: x.fitness)
    for fitness in fitness_range:
        for ind in sorted_individuals:
            if ind.fitness >= fitness:
                selected_individuals.append(ind)
                break

    # for each pair of individuals, make a crossover and save the fitness values
    results = []
    for parent_1 in tqdm(selected_individuals):
        for parent_2 in selected_individuals:
            if parent_1 == parent_2:
                continue
            child = frams_crossover(framsLib, parent_1.genotype, parent_2.genotype)
            fitness = frams_evaluate(framsLib, [child])
            results.append(
                {
                    "fitness_parent_1": parent_1.fitness,
                    "fitness_parent_2": parent_2.fitness,
                    "fitness_child": fitness,
                }
            )

    df = pd.DataFrame(results)
    df.to_csv(f"lab4/f{args.gen_format}/crossovers.csv", index=False)
