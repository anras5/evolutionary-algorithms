import argparse
import os
import sys

import numpy as np
import pandas as pd
from FramsticksLib import FramsticksLib
from deap import creator, base, tools, algorithms, gp

FITNESS_VALUE_INFEASIBLE_SOLUTION = -999999.0


class Branch:
    pass


class Bare:
    pass


def gp_stick(genotype):
    return "X" + genotype


def gp_parenthesis(genotype):
    return "(" + genotype + ")" if genotype != "" and "X" in genotype else ""


def gp_comma(genotype1, genotype2):
    return "(" + genotype1 + "," + genotype2 + ")" if genotype1 != "" and genotype2 != "" else ""


def gp_modifier(modifier):
    def gp_modifier_inner(genotype):
        return modifier + genotype if genotype != "" else ""

    return gp_modifier_inner


def build_pset():
    pset = gp.PrimitiveSetTyped("FRAMS", [], Bare)
    pset.addPrimitive(gp_stick, [Bare], Bare)
    pset.addPrimitive(gp_stick, [Branch], Bare)
    pset.addPrimitive(gp_parenthesis, [Bare], Branch)
    pset.addPrimitive(gp_parenthesis, [Branch], Branch)
    pset.addPrimitive(gp_comma, [Bare, Bare], Branch)
    pset.addPrimitive(gp_comma, [Bare, Branch], Branch)
    pset.addPrimitive(gp_comma, [Branch, Bare], Branch)
    modifiers = ["R", "Q", "C", "L", "W", "F"]
    for modifier in modifiers + list(map(lambda x: x.lower(), (x for x in modifiers))):
        pset.addPrimitive(gp_modifier(modifier), [Bare], Bare, name="mod_Bare_" + modifier)
        pset.addPrimitive(gp_modifier(modifier), [Branch], Bare, name="mod_Branch_" + modifier)

    pset.addTerminal("X", Bare)
    pset.addTerminal("", Bare)
    pset.addTerminal("(X)", Branch)

    return pset


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


def frams_evaluate(frams_lib, pset, individual):
    FITNESS_CRITERIA_INFEASIBLE_SOLUTION = [FITNESS_VALUE_INFEASIBLE_SOLUTION] * len(OPTIMIZATION_CRITERIA)
    try:
        genotype = gp.compile(individual, pset)
    except SyntaxError as e:
        valid = False
    else:
        data = frams_lib.evaluate([genotype])
        # print("Evaluated '%s'" % genotype, 'evaluation is:', data)
        valid = True
        try:
            first_genotype_data = data[0]
            evaluation_data = first_genotype_data["evaluations"]
            default_evaluation_data = evaluation_data[""]
            fitness = [default_evaluation_data[crit] for crit in OPTIMIZATION_CRITERIA]

            # smoothing function for negative fitness values
            if fitness[0] < 0:
                fitness = [-1 / default_evaluation_data["numparts"]]
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


def is_feasible_fitness_value(fitness_value: float) -> bool:
    assert isinstance(
        fitness_value, float
    ), f"feasible_fitness({fitness_value}): argument is not of type float, it is of type {type(fitness_value)}"
    return fitness_value != FITNESS_VALUE_INFEASIBLE_SOLUTION


def is_feasible_fitness_criteria(fitness_criteria: tuple) -> bool:
    return all(is_feasible_fitness_value(fitness_value) for fitness_value in fitness_criteria)


def select_feasible(individuals):
    """
    Filters out only feasible individuals (i.e., with fitness different from FITNESS_VALUE_INFEASIBLE_SOLUTION)
    """
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


def prepareToolbox(frams_lib, OPTIMIZATION_CRITERIA, tournament_size, pset):
    creator.create("FitnessMax", base.Fitness, weights=[1.0] * len(OPTIMIZATION_CRITERIA))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=2, max_=10)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    toolbox.register("evaluate", frams_evaluate, frams_lib, pset)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr, pset=pset)
    toolbox.register("select", selTournament_only_feasible, tournsize=tournament_size)
    return toolbox


def parseArguments():
    parser = argparse.ArgumentParser(
        description='Run this program with "python -u %s" if you want to disable buffering of its output.' % sys.argv[0]
    )
    parser.add_argument(
        "-path",
        type=ensureDir,
        required=True,
        help="Path to Framsticks library without trailing slash.",
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
        "-opt",
        required=True,
        help="optimization criteria: vertpos, velocity, distance, vertvel, lifespan, numjoints, numparts, numneurons, numconnections (or other as long as it is provided by the .sim file and its .expdef). For multiple criteria optimization, separate the names by the comma.",
    )
    parser.add_argument("-max_numparts", type=int, default=None, help="Maximum number of Parts. Default: no limit")
    parser.add_argument(
        "-max_numjoints",
        type=int,
        default=None,
        help="Maximum number of Joints. Default: no limit",
    )
    parser.add_argument(
        "-max_numneurons",
        type=int,
        default=None,
        help="Maximum number of Neurons. Default: no limit",
    )
    parser.add_argument(
        "-max_numconnections",
        type=int,
        default=None,
        help="Maximum number of Neural connections. Default: no limit",
    )
    parser.add_argument(
        "-max_numgenochars",
        type=int,
        default=None,
        help="Maximum number of characters in genotype (including the format prefix, if any). Default: no limit",
    )
    parser.add_argument("-popsize", type=int, default=50, help="Population size, default: 50.")
    parser.add_argument("-generations", type=int, default=5, help="Number of generations, default: 5.")
    parser.add_argument("-tournament", type=int, default=5, help="Tournament size, default: 5.")
    parser.add_argument("-pmut", type=float, default=0.9, help="Probability of mutation, default: 0.9")
    parser.add_argument("-pxov", type=float, default=0.2, help="Probability of crossover, default: 0.2")
    parser.add_argument(
        "-hof_size",
        type=int,
        default=10,
        help="Number of genotypes in Hall of Fame. Default: 10.",
    )
    parser.add_argument(
        "-hof_savefile",
        required=False,
        help="If set, Hall of Fame will be saved in Framsticks file format (recommended extension *.gen).",
    )
    parser.add_argument(
        "-deap_logfile",
        type=str,
        default=None,
        help="If set, DEAP will log to this file.",
    )

    return parser.parse_args()


def ensureDir(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def save_genotypes(filename, OPTIMIZATION_CRITERIA, hof, pset):
    from framsfiles import writer as framswriter

    with open(filename, "w") as outfile:
        for ind in hof:
            keyval = {}
            for i, k in enumerate(OPTIMIZATION_CRITERIA):
                keyval[k] = ind.fitness.values[i]
            outfile.write(
                framswriter.from_collection({"_classname": "org", "genotype": gp.compile(ind, pset), **keyval}))
            outfile.write("\n")
    print("Saved '%s' (%d)" % (filename, len(hof)))


def main():
    global parsed_args, OPTIMIZATION_CRITERIA

    # random.seed(123)  # see FramsticksLib.DETERMINISTIC below, set to True if you want full determinism
    FramsticksLib.DETERMINISTIC = False  # must be set before FramsticksLib() constructor call
    parsed_args = parseArguments()
    print(
        "Argument values:",
        ", ".join(["%s=%s" % (arg, getattr(parsed_args, arg)) for arg in vars(parsed_args)]),
    )
    OPTIMIZATION_CRITERIA = parsed_args.opt.split(",")
    framsLib = FramsticksLib(parsed_args.path, parsed_args.lib, parsed_args.sim)

    pset = build_pset()
    toolbox = prepareToolbox(framsLib, OPTIMIZATION_CRITERIA, parsed_args.tournament, pset=pset)

    pop = toolbox.population(n=parsed_args.popsize)
    hof = tools.HallOfFame(parsed_args.hof_size)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    filter_feasible_for_function = lambda function, fitness_criteria: function(
        list(filter(is_feasible_fitness_criteria, fitness_criteria))
    )
    stats.register(
        "avg",
        lambda fitness_criteria: filter_feasible_for_function(np.mean, fitness_criteria),
    )
    stats.register(
        "stddev",
        lambda fitness_criteria: filter_feasible_for_function(np.std, fitness_criteria),
    )
    stats.register(
        "min",
        lambda fitness_criteria: filter_feasible_for_function(np.min, fitness_criteria),
    )
    stats.register(
        "max",
        lambda fitness_criteria: filter_feasible_for_function(np.max, fitness_criteria),
    )
    pop, log = algorithms.eaSimple(
        pop,
        toolbox,
        cxpb=parsed_args.pxov,
        mutpb=parsed_args.pmut,
        ngen=parsed_args.generations,
        stats=stats,
        halloffame=hof,
        verbose=True,
    )

    if parsed_args.deap_logfile is not None:
        df = pd.DataFrame(log)
        df.to_csv(parsed_args.deap_logfile, index=False)

    print("Best individuals:")
    for ind in hof:
        print(ind.fitness, "\t<--\t", gp.compile(ind, pset))
    if parsed_args.hof_savefile is not None:
        save_genotypes(parsed_args.hof_savefile, OPTIMIZATION_CRITERIA, hof, pset)


if __name__ == "__main__":
    main()
