from term import Term, VariableSymbol, FunctionApplication, get_function_symbols
import term as tm
import z3
from enum import Enum
from pathlib import Path
import sys
from trs_parser import parse

class Relation(Enum):
    """All relations we use (many should just be implications to others)."""
    GREATER = ">"
    EQUAL = "=="
    GEQ = ">="
    GREATER_SUB = ">sub>"
    GREATER_MUL = ">mul>"
    GREATER_COPY = ">copy>"
    EQUAL_VAR = "=var="
    EQUAL_FUN = "=fun="
    def __str__(self):
        return str(self.value)

def var_precedence(var: VariableSymbol) -> z3.Int:
    """
    Given variable var, gives the variable for its precedence.
    """
    return z3.Int(f"[Pred({var})]")

def var_relation(s: any, t: any, rel: Relation) -> z3.Bool:
    """
    Given two things s, t, and relation rel, returns the variable for [s rel t].
    """
    return z3.Bool(f"[{s}{rel}{t}]")

#############
# Task 4(a)
#############


def multiset_equality(x: list[any], y: list[any]) -> z3.ExprRef:
    """
    Implement this!! That is task 4(a).
    Return: a z3 formula that expresses x == y.
    Use the following SMT variables:
    - var_relation(u, v, Relation.EQUAL): boolean variable that expresses x == y
    You need to define your own variables as well.
    We wrote a test below, which you can execute by running python trs_solver.py.
    """

    def count_in_list(value, lst):
        return z3.Sum([z3.If(var_relation(x,value,Relation.EQUAL), 1, 0) for x in lst])

    # For all unique i in x, the number of occurences in x should be equal to the 
    # number of occurences in y.
    return z3.And([count_in_list(i,x) == count_in_list(i,y) for i in set(x)])

#############
# Task 4(b)
#############

def multiset_ordering_greater(x: list[any], y: list[any]) -> z3.ExprRef:
    """
    Implement this!! That is task 4(b).
    Return: a z3 formula that expresses x > y.
    Use the following SMT variables:
    Use these variables over elements of multisets:
    - var_relation(u, v, Relation.GREATER):  boolean variable 
    that expresses x > y
    - var_relation(u, v, Relation.EQUAL): boolean variable that expresses x == y
    You need to define your own variables as well.
    We wrote a test below, which you can execute by running python trs_solver.py.
    """

    n = len(x)
    m = len(y)

    f = [z3.Int(f"f_{i}") for i in range(1,m+1)]

    f_codomain = z3.And([z3.And(1<=f[i],f[i] <= n) for i in range(m)])

    strict = [z3.Bool(f"strict_{i}") for i in range(1,n+1)]
    strict_not_empty = z3.Or([strict[i] for i in range(n)])

    #we define the greater and equal relations here (otherwise we have a problem with getting x[f[i-1]])
    def greater(fi,i):
        return z3.Or([z3.And(var_relation(x[k-1],y[i-1],Relation.GREATER), k == fi) for k in range(1,n+1)])

    def equal(fi,i):
        return z3.Or([z3.And(var_relation(x[k-1],y[i-1],Relation.EQUAL), k == fi) for k in range(1,n+1)])

    #check if f[i] is element of sctrict
    def included(fi):
        return z3.Or([z3.And(strict[k-1],fi == k) for k in range(1, n+1)])

    #the three different properties can be checked for each i:
    def first_property(i):
        return z3.Implies(included(f[i-1]), greater(f[i-1],i))

    def second_property(i):
        return z3.Implies(z3.Not(included(f[i-1])),equal(f[i-1],i))

    def third_property(i):
        return z3.Implies(z3.Or([f[i-1]==f[j-1] for j in range(1,m+1) if j != i]),z3.Or(included(f[i-1])))

    return z3.And(z3.And([z3.And(first_property(i), second_property(i),third_property(i)) for i in range(1,m+1)]), f_codomain, strict_not_empty)



#############
# Task 4(c)
#############

def defining_formula_greater(left: Term, right: Term) -> z3.ExprRef:
    """We're providing this correct implementation for you as a reference."""
    return z3.Or(
        var_relation(left, right, Relation.GREATER_COPY),
        var_relation(left, right, Relation.GREATER_MUL),
        var_relation(left, right, Relation.GREATER_SUB)
    )

def defining_formula_equal_fun(left: Term, right: Term) -> z3.ExprRef:
    """We're also providing this correct implementation for you as a reference."""
    # check that both are function applications
    if not (isinstance(left, FunctionApplication) and isinstance(right, FunctionApplication)):
        return z3.BoolVal(False)
    # check equal arity
    if len(left.terms) != len(right.terms):
        return z3.BoolVal(False)
    return z3.And(
        var_precedence(left.symbol) == var_precedence(right.symbol),
        multiset_equality(left.terms, right.terms)
    )

def defining_formula_equal(left: Term, right: Term) -> z3.ExprRef:
    """Implement this as a part of (c)."""
    return z3.Xor(var_relation(left,right, Relation.EQUAL_FUN),
    var_relation(left,right, Relation.EQUAL_VAR))

def defining_formula_geq(left: Term, right: Term) -> z3.ExprRef:
    """Implement this as a part of (c)."""
    return z3.Xor(var_relation(left,right,Relation.GREATER),var_relation(left,right,Relation.EQUAL))

def defining_formula_greater_sub(left: Term, right: Term) -> z3.ExprRef:
    """Implement this as a part of (c)."""
    if not isinstance(left, FunctionApplication):
        return z3.BoolVal(False)
    return z3.Or([var_relation(i,right,Relation.GEQ) for i in left.terms])

def defining_formula_greater_copy(left: Term, right: Term) -> z3.ExprRef:
    """Implement this as a part of (c)."""
    if not (isinstance(left, FunctionApplication) and isinstance(right, FunctionApplication)):
        return z3.BoolVal(False)
    return z3.And(var_precedence(left.symbol) > var_precedence(right.symbol),z3.And([var_relation(left,i,Relation.GREATER) for i in right.terms]))

def defining_formula_greater_mul(left: Term, right: Term) -> z3.ExprRef:
    """Implement this as a part of (c)."""
    if not (isinstance(left, FunctionApplication) and isinstance(right, FunctionApplication)):
        return z3.BoolVal(False)
    return z3.And(var_precedence(left.symbol) == var_precedence(right.symbol),multiset_ordering_greater(left.terms,right.terms))

def defining_formula_equal_var(left: Term, right: Term) -> z3.ExprRef:
    """Implement this as a part of (c)."""
    if not (isinstance(left, VariableSymbol) and isinstance(right, VariableSymbol)):
        return z3.BoolVal(False)
    return z3.BoolVal(left.name == right.name)


##########################
# STUFF YOU SHOULD NOT CHANGE
##########################


#############
# MPO SOLVING
#############

def mpo_term(u: Term, v: Term, rel: Relation) -> z3.ExprRef:
    """You don't need to change this function."""
    defining_formula = None
    match rel:
        case Relation.GREATER:
            defining_formula = defining_formula_greater(u, v)
        case Relation.EQUAL:
            defining_formula = defining_formula_equal(u, v)
        case Relation.GEQ:
            defining_formula = defining_formula_geq(u, v)
        case Relation.GREATER_SUB:
            defining_formula = defining_formula_greater_sub(u, v)
        case Relation.GREATER_MUL:
            defining_formula = defining_formula_greater_mul(u, v)
        case Relation.GREATER_COPY:
            defining_formula = defining_formula_greater_copy(u, v)
        case Relation.EQUAL_VAR:
            defining_formula = defining_formula_equal_var(u, v)
        case Relation.EQUAL_FUN:
            defining_formula = defining_formula_equal_fun(u, v)
    return var_relation(u, v, rel) == defining_formula

def add_terms_for_rule(left: Term, right: Term, solver: z3.Solver):
    """You don't need to change this function. Adds all terms for a rule in the input."""
    # We first collect all subterms u of s and all subterms v of t, and generate
    # variables [u > v]
    subterms_lhs = tm.get_subterms(left)
    subterms_rhs = tm.get_subterms(right)
    # We require that [s > t] holds:
    solver.assert_and_track(var_relation(left, right, Relation.GREATER), var_relation(left, right, Relation.GREATER))
    # Finally, we generate constraints over each subterm u of s and v of t,
    # creating a defining formula for each variable [u > v].
    # Those constraints are added to the solver we created earlier.
    for u in subterms_lhs:
        for v in subterms_rhs:
            for rel in Relation:
                solver.add(mpo_term(u, v, rel))

def solve(input_file: str):
    """Main solve function for exercise (c) - you don't have to modify this function."""
    lines = Path(input_file).read_text(encoding="utf-8").split("\n")
    trs = parse(lines)
    solver = z3.Solver()

    for (left, right) in trs:
        add_terms_for_rule(left, right, solver)

    # See what the SMT solver says!
    print("Checking with MPO")
    for a in solver.assertions():
        print(a)
    match solver.check():
        case z3.sat:
            print("YES (term Rewriting System is terminating by MPO)")
            model = solver.model()
            print(model)
            function_symbols = get_function_symbols(trs)
            precedences = [(fun, model.evaluate(var_precedence(fun), model_completion=True).as_long()) for fun in function_symbols]
            print("Precedences", precedences)
            if len(trs) > 2:
                print("These are all true statements about subterms of the third rule:")
                # print all true statements about subterms of third rule
                third_rule = trs[2]
                for u in tm.get_subterms(third_rule[0]):
                    for v in tm.get_subterms(third_rule[1]):
                        for rel in Relation:
                            variable = var_relation(u, v, rel)
                            if model[variable] == z3.BoolVal(True):
                                print(variable)
        case z3.unsat:
            print("MAYBE (no solution possible with MPO)")
            print(solver.unsat_core())
        case z3.unknown:
            print("MAYBE (SAT solver could not determine if an MPO solution exists)")
        case _:
            raise TypeError("Argument is not an instance of <class Solver>.")


#############
# TESTING OF MULTISET RELATIONS
#############

def order_on_natural_numbers() -> z3.ExprRef:
    """We need this to test your multiset equality and ordering solutions, don't worry about it."""
    order = []
    # tell the SMT solver that we are using numbers and the semantics are just the normal ones
    for i in range(11):
        for j in range(11):
            order.append(var_relation(i, j, Relation.GREATER) == z3.BoolVal(i > j))
            order.append(var_relation(i, j, Relation.GEQ) == z3.BoolVal(i >= j))
            order.append(var_relation(i, j, Relation.EQUAL) == z3.BoolVal(i == j))
    return z3.And(*order)

def test_multiset_equality():
    """Test for exercise (a)."""
    o = order_on_natural_numbers()
    assert z3.Solver().check(z3.And(o, multiset_equality([3, 3, 1, 1], [1, 3, 3, 1]))) == z3.sat
    assert z3.Solver().check(z3.And(o, multiset_equality([3, 1, 1, 1], [1, 3, 3, 1]))) == z3.unsat
    assert z3.Solver().check(z3.And(o, multiset_equality([], []))) == z3.sat
    assert z3.Solver().check(z3.And(o, multiset_equality([1, 2, 3, 4], [4, 3, 2, 1]))) == z3.sat
    assert z3.Solver().check(z3.And(o, multiset_equality([1, 2, 3, 4], [4, 3, 2, 1, 4]))) == z3.unsat
    print("multiset equality test passed")


def test_multiset_ordering():
    """Test for exercise (b)."""
    o = order_on_natural_numbers()
    assert z3.Solver().check(z3.And(o, multiset_ordering_greater([5, 3, 1, 1, 1], [4, 3, 3, 1]))) == z3.sat
    assert z3.Solver().check(z3.And(o, multiset_ordering_greater([10, 5, 3, 1, 1, 1], [10, 4, 3, 3, 1]))) == z3.sat
    assert z3.Solver().check(z3.And(o, multiset_ordering_greater([], []))) == z3.unsat
    assert z3.Solver().check(z3.And(o, multiset_ordering_greater([1], [1]))) == z3.unsat
    assert z3.Solver().check(z3.And(o, multiset_ordering_greater([2], [1]))) == z3.sat 
    assert z3.Solver().check(z3.And(o, multiset_ordering_greater([1, 1, 3], [1, 2, 2]))) == z3.sat
    assert z3.Solver().check(z3.And(o, multiset_ordering_greater([1], [2]))) == z3.unsat
    assert z3.Solver().check(z3.And(o, multiset_ordering_greater([4, 3, 3, 1], [5, 3, 1, 1, 1]))) == z3.unsat
    assert z3.Solver().check(z3.And(o, multiset_ordering_greater([10, 4, 3, 3, 1], [10, 5, 3, 1, 1, 1]))) == z3.unsat
    assert z3.Solver().check(z3.And(o, multiset_ordering_greater([1, 1], [1, 1]))) == z3.unsat
    assert z3.Solver().check(z3.And(o, multiset_ordering_greater([1, 2, 3, 4], [4, 3, 2, 1]))) == z3.unsat
    print("multiset ordering test passed")


#############
# ENTRY POINT OF PYTHON FILE
#############

def main():
    # EXERCISE (A).
    test_multiset_equality()
    # EXERCISE (B).
    test_multiset_ordering()
    if len(sys.argv) == 2: #it was set to 1 so I changed it
        # EXERCISE (C).
        solve(sys.argv[1])
    else:
        print("Please provide exactly one file name (the .trs input file.)")

if __name__ == "__main__":
    main()
