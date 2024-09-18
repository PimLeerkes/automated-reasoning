# Five couples want to organize a dinner. 
from z3 import *
from tabulate import tabulate

ROUNDS = 5
PPL = 10
HOUSES = int(PPL/2)
COUPLES = HOUSES

def flatten(xss):
    return [x for xs in xss for x in xs]

def invert_2d_list(l):
    res = []
    for i in range(len(l[0])):
        sublist =  []
        for j in range(len(l)):
            sublist.append(l[j][i])
        res.append(sublist)
    return res

V_people_locations = [[Int(f"p{p}_r{r}_c") for r in range(ROUNDS)] for p in range(PPL)]
V_people_locations_inverted = invert_2d_list(V_people_locations)
F_people_locations_bound = [And([And(loc >= 0, loc < HOUSES) for loc in p]) for p in V_people_locations]
V_people_couples = [Int(f"p{p}_c") for p in range(PPL)]
F_people_couples_bound = [And(couple >= 0, couple < COUPLES) for couple in V_people_couples]

# Each couple consists of two people living together in one house, so there are five houses in total. 
def z3_count(x:int, l:list[ArithRef]):
    """Return the count of x in l.
    Example usage z3_count(4, list_of_vars) == 2. '4' occurs twice in list_of_vars."""
    return Sum([x_ == x for x_ in l])

def flatten(xss):
    return [x for xs in xss for x in xs]

F_couple_is_two_people = [z3_count(x, V_people_couples) == 2 for x in range(COUPLES)]

# The dinner consists of five rounds. 

V_round_couples_a = [Int(f"r{r}_ca") for r in range(ROUNDS)]
V_round_couples_b = [Int(f"r{r}_cb") for r in range(ROUNDS)]
V_round_couples = V_round_couples_a + V_round_couples_b
F_round_couples_bound = [And(0 <= rc, rc < COUPLES) for rc in (V_round_couples)]

# Each round is held in two houses at the same time.
F_each_round_two_houses = [rca != rcb for (rca, rcb) in zip(V_round_couples_a, V_round_couples_b)]

# , with five people in each house(/couple).
def num_people_in_house_at_round(r:int, hc:int):
    ppl_locs = V_people_locations_inverted[r]
    return z3_count(hc, ppl_locs)

F_five_people_in_each_house_every_round = [
    And([
        Implies(V_round_couples_a[r_no] == c_no, num_people_in_house_at_round(r_no, c_no) == 5),
        Implies(V_round_couples_b[r_no] == c_no, num_people_in_house_at_round(r_no, c_no) == 5),
        ])
    for r_no in range(ROUNDS) for c_no in range(COUPLES)
]

# Every couple hosts two rounds in their house, 

F_every_couple_two_rounds = [
    z3_count(c_no, V_round_couples) == 2
    for c_no in range(COUPLES)
]

# for which both hosts have to be present.

F_couple_present_at_own_party = [
    Implies(And(V_round_couples[r_no] == c_no, V_people_couples[p_no] == c_no), 
            V_people_locations[p_no][r_no] == c_no)
    for r_no in range(ROUNDS) 
    for c_no in range(COUPLES)
    for p_no in range(PPL)
]
#[print(clause) for clause in F_couple_present_at_own_party[:100]]

# No participant may be in the same house with another participant for all five rounds. 

# Between the rounds, participants may move from one house to another.

# ONLY F HERE
V_all_vars = flatten(V_people_locations) +\
V_people_couples +\
V_round_couples

# ONLY V HERE
phi = F_people_locations_bound +\
F_people_couples_bound +\
F_couple_is_two_people +\
F_round_couples_bound +\
F_each_round_two_houses +\
F_five_people_in_each_house_every_round +\
F_every_couple_two_rounds +\
F_couple_present_at_own_party

s = Solver()
s.add(phi)
s.check()
m = s.model()
res = {var: m.evaluate(var) for var in V_all_vars}


###### printing
print("Locations")
people_location_values = [[str(res[p]) for p in r] for r in V_people_locations_inverted]
people_location_values_inverted = invert_2d_list(people_location_values)
print(tabulate(people_location_values, headers = [f"p{p}" for p in range(PPL)]))
print("Number of parties hosted")


#solve(phi)

# On top of these requirements, there are four desired properties:
# (A) Every two people among the ten participants meet each other at least once.

# (B) Every two people among the ten participants meet each other at most three times.

# (C) Couples never meet outside their own houses.

# (D) No person can be a guest in the same house twice.
