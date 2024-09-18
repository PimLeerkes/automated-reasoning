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

F_no_same_house_always = [
    Not(And([
        V_people_locations[p1_no][r_no] == V_people_locations[p2_no][r_no] for r_no in range(ROUNDS)
    ]))
    for p1_no in range(PPL) for p2_no in range(PPL) if p1_no != p2_no]
#print(F_no_same_house_always[0:3])

# (Between the rounds, participants may move from one house to another. ) We get it for free! :D

# On top of these requirements, there are four desired properties:
# (A) Every two people among the ten participants meet each other at least once.

def number_of_meetings(p1_no, p2_no):
    return Sum([V_people_locations[p1_no][r_no] == V_people_locations[p2_no][r_no] for r_no in range(ROUNDS)])

F_A_meet_each_other_at_least_once = [
    number_of_meetings(p1_no, p2_no) >= 1 for p1_no in range(PPL) for p2_no in range(PPL) if p1_no != p2_no
]
#print(F_A_meet_each_other_at_least_once[0:3])

# (B) Every two people among the ten participants meet each other at most three times.

F_B_meet_each_other_at_most_thrice = [
    number_of_meetings(p1_no, p2_no) <= 3 for p1_no in range(PPL) for p2_no in range(PPL) if p1_no != p2_no
]

# (C) Couples never meet outside their own houses.
# True iff they meet exactly twice, given that they host two parties at which both of them have to be present.
F_C_couples_never_meet_outside_own_houses = [
    number_of_meetings(p1_no, p2_no) == 2 for p1_no in range(PPL) for p2_no in range(PPL) if p1_no != p2_no
]

def num_times_p_in_cs_house(p_no, c_no):
    """The number of times that p_no has been in c_no's house."""
    locs_of_p = V_people_locations[p_no]
    return z3_count(c_no, locs_of_p)


# (D) No person can be a guest in the same house twice.
F_D_no_guest_same_house_twice = [
    Implies(V_people_couples[p_no] != c_no, num_times_p_in_cs_house(p_no, c_no) < 2)
    for p_no in range(PPL) for c_no in range(COUPLES)
]
#print(F_D_no_guest_same_house_twice[0:3])

# ONLY F HERE
V_all_vars = flatten(V_people_locations) +\
V_people_couples +\
V_round_couples

### Definitions of questions.
F_ACD = F_A_meet_each_other_at_least_once + F_C_couples_never_meet_outside_own_houses + F_D_no_guest_same_house_twice
F_AC = F_A_meet_each_other_at_least_once + F_C_couples_never_meet_outside_own_houses
F_AD = F_A_meet_each_other_at_least_once + F_D_no_guest_same_house_twice
F_BCD = F_B_meet_each_other_at_most_thrice + F_C_couples_never_meet_outside_own_houses + F_D_no_guest_same_house_twice
###

# ONLY V HERE
phi = F_people_locations_bound +\
F_people_couples_bound +\
F_couple_is_two_people +\
F_round_couples_bound +\
F_each_round_two_houses +\
F_five_people_in_each_house_every_round +\
F_every_couple_two_rounds +\
F_couple_present_at_own_party +\
F_no_same_house_always +\
F_AD # Change this per question


# Results (N.B. 'model not available' means unsat):
# A /\ C /\ D unsat | Correct
# A /\ C            | Unsat
# A /\ D            | Sat, see proof below:
# B /\ C /\ D       | Unsat

# Proof for A /\ D sat:
# People and locations per round
#       r0    r1    r2    r3    r4
# --  ----  ----  ----  ----  ----
# p0     2     4     4     1     3
# p1     0     2     1     3     3
# p2     2     2     4     1     0
# p3     2     4     1     3     3
# p4     0     2     1     1     3
# p5     2     2     4     3     0
# p6     0     4     4     1     3
# p7     0     2     4     3     0
# p8     2     4     1     1     0
# p9     0     4     1     3     0
# l1     2     4     1     3     0
# l2     0     2     4     1     3

# People belonging to couples
#   p0    p1    p2    p3    p4    p5    p6    p7    p8    p9
# ----  ----  ----  ----  ----  ----  ----  ----  ----  ----
#    4     3     2     3     1     2     4     0     1     0

s = Solver()
s.add(phi)
print("Solving")
s.check()
m = s.model()
res = {var: m.evaluate(var) for var in V_all_vars}


###### printing
print("People and locations per round")
people_location_values = [[str(res[p]) for p in r] for r in V_people_locations_inverted]
party_locations_a = [str(res[loc]) for loc in V_round_couples_a]
party_locations_b = [str(res[loc]) for loc in V_round_couples_b]




labels = [f"p{p}" for p in range(PPL)] + ["l1", "l2"]
#people_location_values.insert(0, labels)
people_location_values_inverted = invert_2d_list(people_location_values)
people_location_values_inverted.append(party_locations_a)
people_location_values_inverted.append(party_locations_b)
l2 = invert_2d_list(people_location_values_inverted)
l2.insert(0, labels)
l3 = invert_2d_list(l2)

print(tabulate(l3, headers = [f"r{r}" for r in range(ROUNDS)]))

print("\nPeople belonging to couples")
couples_list = invert_2d_list([str(res[v]) for v in V_people_couples])
print(tabulate(couples_list, headers=[f"p{x}" for x in range(PPL)]))
