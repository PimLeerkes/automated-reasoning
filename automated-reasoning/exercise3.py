from z3 import *
from pretty_printer import solve_and_print

HOUSES, COUPLES, ROUNDS = 5, 5, 5
PEOPLE = 10
PEOPLE_PER_ROUND = 5


P = [Int(f"p_{i}") for i in range(PEOPLE)]

R_a = [Int(f"r_a_{i}") for i in range(ROUNDS)]
R_b = [Int(f"r_b_{i}") for i in range(ROUNDS)]

PR = [[Int(f"p_{i}_{j}") for i in range(PEOPLE)] for j in range(ROUNDS)]


#We make the couples:
#for i in range(COUPLES):
#    P[i*2] = Int(i)
#    P[i*2 + 1] = Int(i)

#sum_is_two = [Sum(R_a_b[j] == i for j in range(len(R_a + R_b)))] == 2


each_round_in_two_houses = [And(Not(R_a[i] == R_b[i]), Or(R_a[i] == 0, R_a[i] == 1, R_a[i] == 2, R_a[i] == 3, R_a[i] == 4), Or(R_b[i] == 0, R_b[i] == 1, R_b[i] == 2, R_b[i] == 3, R_b[i] == 4)) for i in range(ROUNDS)]

each_round_has_five_people_per_house = [And(Sum(PR[i]) == 5, And([Or(PR[i][j] == 0, PR[i][j] == 1) for j in range(PEOPLE)])) for i in range(ROUNDS)]

every_couple_hosts_two_rounds_in_their_house = [And(Sum(Sum([R_a[j] == i for j in range(ROUNDS)]),Sum([R_b[j] == i for j in range(ROUNDS)])) == 2) for i in range(HOUSES)]

<<<<<<< HEAD
=======


>>>>>>> fb77dcd00962cb8bf2033430faba200c96f116f6
phi = each_round_in_two_houses + each_round_has_five_people_per_house + every_couple_hosts_two_rounds_in_their_house

solve(phi)

solve_and_print(P, R_a, R_b, PR, phi, all_vars=True, pretty=True)
