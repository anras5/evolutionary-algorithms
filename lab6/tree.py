from deap import gp


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

    return pset


pset = build_pset()
expr = gp.genFull(pset, min_=3, max_=5)
tree = gp.PrimitiveTree(expr)
print(tree)
ans = gp.compile(tree, pset)
print(ans)
