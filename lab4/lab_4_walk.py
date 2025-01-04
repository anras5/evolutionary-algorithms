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


def frams_mutate(frams_lib: FramsticksLib, individual: str):
    return frams_lib.mutate([individual])


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
        required=True,
        default=10,
        help="Number of iterations from the main evolution (ran with run.sh)."
    )
    parser.add_argument(
        "--generations",
        type=int,
        required=True,
        default=130,
        help="Number of generations in each iteration from the main evolution (ran with run.sh)."
    )
    args = parser.parse_args()
    FramsticksLib.DETERMINISTIC = False
    framsLib = FramsticksLib(args.path, frams_lib_name=args.lib, sim_settings_files=args.sim)

    # iterate over saved individuals and save them
    for gen_format in [0, 1, 4, 9]:

        individuals = []
        for iteration in range(1, args.iterations + 1):
            for generation in range(1, args.generations + 1):
                with open(f"lab4/f{gen_format}/genotypes/{iteration}/{generation}.gen", "r") as f:
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

        print(f"Genotype: f{gen_format}")
        print(f"{len(individuals)=}")
        # get min and max fitness
        min_fitness = min([i.fitness for i in individuals])
        max_fitness = max([i.fitness for i in individuals])
        print(f"{min_fitness=}, {max_fitness=}")

        # divide the (min, max) range into 20 equal parts
        fitness_range = [min_fitness + (max_fitness - min_fitness) / 20 * i for i in range(21)]
        # save one individual for each of the 20 parts
        selected_individuals = []
        sorted_individuals = sorted(individuals, key=lambda x: x.fitness)
        for fitness in fitness_range:
            for ind in sorted_individuals:
                if ind.fitness >= fitness:
                    selected_individuals.append(ind)
                    break

        # mutate each individual in selected_individuals 30 times (random walk) and save the fitness values
        results = {"fitness_original": []}
        results.update({f"fitness_{i}": [] for i in range(1, 31)})
        for ind in tqdm(selected_individuals):
            results["fitness_original"].append(ind.fitness)
            current_genotype = ind.genotype
            for i in range(1, 31):
                current_genotype = frams_mutate(framsLib, current_genotype)[0]
                evaluation = frams_evaluate(framsLib, [current_genotype])
                while evaluation == FITNESS_VALUE_INFEASIBLE_SOLUTION:
                    new_genotype = frams_mutate(framsLib, current_genotype)[0]
                    evaluation = frams_evaluate(framsLib, [new_genotype])

                results[f"fitness_{i}"].append(evaluation)

        df = pd.DataFrame(results)
        df.to_csv(f"lab4/f{gen_format}/random-walk.csv", index=False)
