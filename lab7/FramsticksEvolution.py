import argparse
import os
import random
import sys
from copy import deepcopy

import numpy as np
import pandas as pd
from FramsticksLib import FramsticksLib
from deap import creator, base, tools

FITNESS_VALUE_INFEASIBLE_SOLUTION = -999999.0
OPTIMIZATION_CRITERIA_NUMBER = 2


def genotype_within_constraint(genotype, dict_criteria_values, criterion_name, constraint_value):
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
    FITNESS_CRITERIA_INFEASIBLE_SOLUTION = [FITNESS_VALUE_INFEASIBLE_SOLUTION] * OPTIMIZATION_CRITERIA_NUMBER
    genotype = individual[0]
    data = frams_lib.evaluate([genotype])
    # print("Evaluated '%s'" % genotype, 'evaluation is:', data)
    valid = True
    try:
        first_genotype_data = data[0]
        evaluation_data = first_genotype_data["evaluations"]
        default_evaluation_data = evaluation_data[""]

        # fitness = [default_evaluation_data[crit] for crit in OPTIMIZATION_CRITERIA]

        # calculate the distance between the first and last recording
        x1, y1 = default_evaluation_data["data->bodyrecording"][0][:2]
        x2, y2 = default_evaluation_data["data->bodyrecording"][-1][:2]
        distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

        # calculate the max "jump" height from the recordings
        max_height = max([rec[2] for rec in default_evaluation_data["data->bodyrecording"]])
        min_height = min([rec[2] for rec in default_evaluation_data["data->bodyrecording"]])
        height_difference = max_height - min_height

        if OPTIMIZATION_CRITERIA_NUMBER == 1:
            fitness = [distance]
            # fitness = [height_difference]
        else:
            fitness = [distance, height_difference]

    except (KeyError, TypeError) as e:
        valid = False
        print(
            'Problem "%s" so could not evaluate genotype "%s", hence assigned it a special ("infeasible solution") fitness value: %s'
            % (str(e), genotype, FITNESS_CRITERIA_INFEASIBLE_SOLUTION)
        )
    if valid:
        default_evaluation_data["numgenocharacters"] = len(genotype)  # for consistent constraint checking below
        valid &= genotype_within_constraint(genotype, default_evaluation_data, "numparts", parsed_args.max_numparts)
        valid &= genotype_within_constraint(genotype, default_evaluation_data, "numjoints", parsed_args.max_numjoints)
        valid &= genotype_within_constraint(genotype, default_evaluation_data, "numneurons", parsed_args.max_numneurons)
        valid &= genotype_within_constraint(
            genotype, default_evaluation_data, "numconnections", parsed_args.max_numconnections
        )
        valid &= genotype_within_constraint(
            genotype, default_evaluation_data, "numgenocharacters", parsed_args.max_numgenochars
        )
    if not valid:
        fitness = FITNESS_CRITERIA_INFEASIBLE_SOLUTION
    return fitness


def frams_crossover(frams_lib, individual1, individual2):
    geno1 = individual1[0]
    geno2 = individual2[0]
    individual1[0] = frams_lib.crossOver(geno1, geno2)
    individual2[0] = frams_lib.crossOver(geno1, geno2)
    return individual1, individual2


def frams_mutate(frams_lib, individual):
    individual[0] = frams_lib.mutate([individual[0]])[0]
    return (individual,)


def frams_getsimplest(frams_lib, genetic_format, initial_genotype):
    return initial_genotype if initial_genotype is not None else frams_lib.getSimplest(genetic_format)


def is_feasible_fitness_value(fitness_value: float) -> bool:
    assert isinstance(fitness_value, float), (
        f"feasible_fitness({fitness_value}): argument is not of type float, it is of type {type(fitness_value)}"
    )
    return fitness_value != FITNESS_VALUE_INFEASIBLE_SOLUTION


def is_feasible_fitness_criteria(fitness_criteria: tuple) -> bool:
    return all(is_feasible_fitness_value(fitness_value) for fitness_value in fitness_criteria)


def select_feasible(individuals):
    """
    Filters out only feasible individuals (i.e., with fitness different from FITNESS_VALUE_INFEASIBLE_SOLUTION)
    """
    # for ind in individuals:
    # print(ind.fitness.values, ind)
    feasible_individuals = [ind for ind in individuals if is_feasible_fitness_criteria(ind.fitness.values)]
    count_all = len(individuals)
    count_infeasible = count_all - len(feasible_individuals)
    if count_infeasible != 0:
        print(
            "Selection: ignoring %d infeasible solution%s in a population of size %d"
            % (count_infeasible, "s" if count_infeasible > 1 else "", count_all)
        )
    return feasible_individuals


def selTournament_only_feasible(individuals, k, tournsize):
    return tools.selTournament(select_feasible(individuals), k, tournsize=tournsize)


def selNSGA2_only_feasible(individuals, k, save, iteration=None):
    selected_individuals = tools.selNSGA2(
        select_feasible(individuals), k
    )  # this method (unfortunately) decreases population size permanently each time an infeasible solution is removed

    # save genotypes
    if save:
        genotypes_save_dir = parsed_args.genotypes_save_dir
        if parsed_args.load_file:
            iteration = int(parsed_args.load_file.split("/")[-1].split(".")[0]) + iteration
            save_genotypes(f"{genotypes_save_dir}/{iteration}.gen", selected_individuals)
        else:
            save_genotypes(f"{genotypes_save_dir}/{iteration}.gen", selected_individuals)
    return selected_individuals


def init_population(pcls, ind_init, filename):
    individuals = []
    with open(filename, "r") as f:
        ind = None
        genotype_line = False
        for line in f:
            # start of a new individual
            if line.startswith("org:"):
                ind = ""

            # start of genotype
            if line.startswith("genotype:"):
                genotype = line.split(":")[1].strip()
                # ~ starts multiline genotype for f0 and fH
                if genotype == "~":
                    genotype_line = True
                    continue
                else:
                    ind = line[9:].strip()  # so we skip "genotype:"
            if genotype_line and line.strip() == "~":
                genotype_line = False
            if genotype_line:
                ind += line

            # end of individual
            if line == "\n":
                individuals.append(ind)

    return pcls(ind_init([ind]) for ind in individuals)


def prepareToolbox(frams_lib, tournament_size, genetic_format, initial_genotype, load_file):
    creator.create("FitnessMax", base.Fitness, weights=[1.0] * OPTIMIZATION_CRITERIA_NUMBER)
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("attr_simplest_genotype", frams_getsimplest, frams_lib, genetic_format, initial_genotype)

    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_simplest_genotype, 1)
    if not load_file:
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    else:
        toolbox.register("population_guess", init_population, list, creator.Individual, load_file)

    toolbox.register("evaluate", frams_evaluate, frams_lib)
    toolbox.register("mate", frams_crossover, frams_lib)
    toolbox.register("mutate", frams_mutate, frams_lib)
    if OPTIMIZATION_CRITERIA_NUMBER <= 1:
        toolbox.register("select", selTournament_only_feasible, tournsize=tournament_size)
    else:
        toolbox.register("select", selNSGA2_only_feasible)
    return toolbox


def parseArguments():
    parser = argparse.ArgumentParser(
        description='Run this program with "python -u %s" if you want to disable buffering of its output.' % sys.argv[0]
    )
    parser.add_argument(
        "-path", type=ensureDir, required=True, help="Path to Framsticks library without trailing slash."
    )
    parser.add_argument(
        "-lib",
        required=False,
        help='Library name. If not given, "frams-objects.dll" (or .so or .dylib) is assumed depending on the platform.',
    )
    parser.add_argument(
        "-sim",
        required=False,
        default="eval-allcriteria.sim",
        help='The name of the .sim file with settings for evaluation, mutation, crossover, and similarity estimation. If not given, "eval-allcriteria.sim" is assumed by default. Must be compatible with the "standard-eval" expdef. If you want to provide more files, separate them with a semicolon \';\'.',
    )
    parser.add_argument(
        "-genformat",
        required=False,
        help="Genetic format for the simplest initial genotype, for example 4, 9, or B. If not given, f1 is assumed.",
    )
    parser.add_argument(
        "-initialgenotype",
        required=False,
        help="The genotype used to seed the initial population. If given, the -genformat argument is ignored.",
    )
    parser.add_argument("-popsize", type=int, default=50, help="Population size, default: 50.")
    parser.add_argument("-generations", type=int, default=5, help="Number of generations, default: 5.")
    parser.add_argument("-tournament", type=int, default=5, help="Tournament size, default: 5.")
    parser.add_argument("-pmut", type=float, default=0.9, help="Probability of mutation, default: 0.9")
    parser.add_argument("-pxov", type=float, default=0.2, help="Probability of crossover, default: 0.2")
    parser.add_argument("-hof_size", type=int, default=10, help="Number of genotypes in Hall of Fame. Default: 10.")
    parser.add_argument(
        "-hof_savefile",
        required=False,
        help="If set, Hall of Fame will be saved in Framsticks file format (recommended extension *.gen).",
    )
    parser.add_argument("-max_numparts", type=int, default=None, help="Maximum number of Parts. Default: no limit")
    parser.add_argument("-max_numjoints", type=int, default=None, help="Maximum number of Joints. Default: no limit")
    parser.add_argument("-max_numneurons", type=int, default=None, help="Maximum number of Neurons. Default: no limit")
    parser.add_argument(
        "-max_numconnections", type=int, default=None, help="Maximum number of Neural connections. Default: no limit"
    )
    parser.add_argument(
        "-max_numgenochars",
        type=int,
        default=None,
        help="Maximum number of characters in genotype (including the format prefix, if any). Default: no limit",
    )

    parser.add_argument("-deap_logfile", type=str, default=None, help="If set, DEAP will log to this file.")

    parser.add_argument(
        "-genotypes_save_dir", type=str, default=None, help="Directory to save genotypes in each iteration."
    )

    parser.add_argument(
        "-load_file", type=str, default="", help="If set, load the population from the given file."
    )

    return parser.parse_args()


def ensureDir(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def save_genotypes(filename, hof):
    from framsfiles import writer as framswriter

    with open(filename, "w") as outfile:
        for ind in hof:
            keyval = {}
            for i, k in enumerate(range(OPTIMIZATION_CRITERIA_NUMBER)):
                keyval[k] = ind.fitness.values[i]
            outfile.write(framswriter.from_collection({"_classname": "org", "genotype": ind[0], **keyval}))
            outfile.write("\n")
    print("Saved '%s' (%d)" % (filename, len(hof)))


def evolution(population, toolbox, mutpb, ngen, stats=None, halloffame=None, verbose=__debug__):
    """This algorithm reproduce the simplest evolutionary algorithm as
    presented in chapter 7 of [Back2000]_.

    :param population: A list of individuals.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param mutpb: The probability of mutating an individual.
    :param ngen: The number of generation.
    :param stats: A :class:`~deap.tools.Statistics` object that is updated
                  inplace, optional.
    :param halloffame: A :class:`~deap.tools.HallOfFame` object that will
                       contain the best individuals, optional.
    :param verbose: Whether to log the statistics.
    :returns: The final population
    :returns: A class:`~deap.tools.Logbook` with the statistics of the
              evolution
    """
    logbook = tools.Logbook()
    logbook.header = ["gen", "nevals"] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen + 1):
        # Select the next generation individuals
        parents = toolbox.select(population, len(population), save=False)

        # Apply crossover and mutation on the offspring
        # Crossover
        parents_indexed = [(i, parent) for i, parent in enumerate(parents)]
        offspring = []
        # Choose pairs of parents
        pairs_of_parents = []
        for i in range(len(parents_indexed)):  # we want as many pairs as the number of parents
            parents_temp = deepcopy(parents_indexed)
            # create a tournament of two individuals (parents) and choose the one with lower "i"
            # which is the index of the parent after sorting parents using nsga2
            parent1 = min(random.sample(parents_temp, 2), key=lambda x: x[0])
            parents_temp.remove(parent1)  # don't choose the same parent twice
            parent2 = min(random.sample(parents_temp, 2), key=lambda x: x[0])
            pairs_of_parents.append((parent1[1], parent2[1]))

        # Create offspring
        for parent1, parent2 in pairs_of_parents:
            offspring.append(toolbox.mate(parent1, parent2)[0])
            del offspring[-1].fitness.values

        # Mutate
        for i in range(len(offspring)):
            if random.random() < mutpb:
                (offspring[i],) = toolbox.mutate(offspring[i])
                del offspring[i].fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)

        intermediate_population = parents + offspring
        population = toolbox.select(intermediate_population, len(population), save=True, iteration=gen)

        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

    return population, logbook


def main():
    global parsed_args

    FramsticksLib.DETERMINISTIC = False
    parsed_args = parseArguments()
    print("Argument values:", ", ".join(["%s=%s" % (arg, getattr(parsed_args, arg)) for arg in vars(parsed_args)]))
    framsLib = FramsticksLib(parsed_args.path, parsed_args.lib, parsed_args.sim)
    toolbox = prepareToolbox(
        framsLib,
        parsed_args.tournament,
        "1" if parsed_args.genformat is None else parsed_args.genformat,
        parsed_args.initialgenotype,
        parsed_args.load_file
    )
    if parsed_args.load_file:
        pop = toolbox.population_guess()
    else:
        pop = toolbox.population(n=parsed_args.popsize)
    hof = tools.HallOfFame(parsed_args.hof_size)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    filter_feasible_for_function = lambda function, fitness_criteria: function(
        list(filter(is_feasible_fitness_criteria, fitness_criteria))
    )
    stats.register("avg", lambda fitness_criteria: filter_feasible_for_function(np.mean, fitness_criteria))
    stats.register("stddev", lambda fitness_criteria: filter_feasible_for_function(np.std, fitness_criteria))
    stats.register("min", lambda fitness_criteria: filter_feasible_for_function(np.min, fitness_criteria))
    stats.register("max", lambda fitness_criteria: filter_feasible_for_function(np.max, fitness_criteria))
    pop, log = evolution(
        pop,
        toolbox,
        mutpb=parsed_args.pmut,
        ngen=parsed_args.generations,
        stats=stats,
        halloffame=hof,
        verbose=True,
    )

    if parsed_args.deap_logfile is not None and OPTIMIZATION_CRITERIA_NUMBER == 1:
        df = pd.DataFrame(log)
        df.to_csv(parsed_args.deap_logfile, index=False)

    print("Best individuals:")
    for ind in hof:
        print(ind.fitness, "\t<--\t", ind[0])
    if parsed_args.hof_savefile is not None:
        save_genotypes(parsed_args.hof_savefile, hof)


if __name__ == "__main__":
    main()
