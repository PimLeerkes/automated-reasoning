from z3 import *

HOUSES, COUPLES, ROUNDS = 5, 5, 5
PEOPLE = 10
PEOPLE_PER_ROUND = 5


P = [Int(f"p_{i}")for i in range(PEOPLE)]
R_a = [Int(f"R_a_{i}")for i in range(ROUNDS)]
R_b = [Int(f"R_b_{i}")for i in range(ROUNDS)]

#We make the couples:
for i in range(COUPLES):
    P[i*2] = i
    P[i*2 + 1] = i

each_round_in_two_houses = [And(Not(R_a[i] == R_b[i]), Or(R_a[i] == 0, R_a[i] == 1, R_a[i] == 2, R_a[i] == 3, R_a[i] == 4), Or(R_b[i] == 0, R_b[i] == 1, R_b[i] == 2, R_b[i] == 3, R_b[i] == 4)) for i in range(ROUNDS)]

each_round_has_five_people_per_house = [And() for i in range(ROUNDS)]


phi = each_round_in_two_houses

solve(phi)