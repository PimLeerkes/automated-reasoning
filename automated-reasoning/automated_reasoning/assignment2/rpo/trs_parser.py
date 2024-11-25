"""Parser for term rewriting systems."""
from term import FunctionApplication, VariableSymbol

def parse_term(desc: str, variables: set[str], sig: set[str], pos: int):
    """Parses a single term"""
    i = pos + 1
    while i < len(desc) and desc[i].isalnum():
        i += 1
    name = desc[pos:i]
    while i < len(desc) and desc[i] == " ":
        i += 1
    if i == len(desc) or desc[i] == "," or desc[i] == ")":
        x = VariableSymbol(name)
        variables.add(x)
        return (x, i)
    if desc[i] != "(":
        raise RuntimeError("Unexpected symbol at position " + str(i) + " of " + desc)
    i += 1
    args = []
    while i < len(desc) and desc[i] != ")":
        if desc[i] != " " and desc[i] != ",":
            (arg, i) = parse_term(desc, variables, sig, i)
            args += [arg]
        else:
            i += 1
    if i == len(desc):
        raise RuntimeError("Unexpected end of line (unclosed bracket) in " + desc)
    return (FunctionApplication(name, args), i + 1)

def parse(lines: str):
    """Parses a term rewriting system."""
    rules = [line.split("->") for line in lines]
    rules = [(r[0].strip(), r[1].strip()) for r in rules if len(r) == 2]
    variables = set()
    sig = set()
    rules = [
        (parse_term(r[0], variables, sig, 0)[0], parse_term(r[1], variables, sig, 0)[0])
        for r in rules
    ]
    return rules
