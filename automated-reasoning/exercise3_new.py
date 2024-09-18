# Five couples want to organize a dinner. 
from z3 import *
from dataclasses import dataclass

ROUNDS = 5
PPL = 10
HOUSES = int(PPL/2)
COUPLES = HOUSES

V_people_locations = [[Int(f"p{p}_r{r}_c") for r in range(ROUNDS)] for p in range(PPL)]
F_people_locations_bound = [And([And(loc >= 0, loc < HOUSES) for loc in p]) for p in V_people_locations]
V_people_couples = [Int(f"p{p}_c") for p in range(PPL)]
F_people_couples_bound = [And(couple >= 0, couple < COUPLES) for couple in V_people_couples]

# Each couple consists of two people living together in one house, so there are five houses in total. 
def z3_count(x, l):
    """Return the count of x in l."""
    return Sum([x_ == x for x_ in l])

def flatten(xss):
    return [x for xs in xss for x in xs]

F_couple_is_two_people = [z3_count(x, V_people_couples) == 2 for x in range(COUPLES)]

# The dinner consists of five rounds. Each round is held in two houses at the same time, with five people in each house.

V_round_couples_a = [Int(f"r{r}_ca") for r in ]
V_round_couples_b = []

# Every couple hosts two rounds in their house, for which both hosts have to be present. 

# No participant may be in the same house with another participant for all five rounds. 

# Between the rounds, participants may move from one house to another.

phi = F_people_locations_bound + F_people_couples_bound + F_couple_is_two_people

solve(phi)

# On top of these requirements, there are four desired properties:
# (A) Every two people among the ten participants meet each other at least once.

# (B) Every two people among the ten participants meet each other at most three times.

# (C) Couples never meet outside their own houses.

# (D) No person can be a guest in the same house twice.
