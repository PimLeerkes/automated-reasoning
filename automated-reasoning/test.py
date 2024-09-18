from z3 import *

BUSSES = 8
W_BUS = 8000

SAFFRON = 4
W_SAFFRON = 700
S = [[Bool(f"s_{i}_{j}") for j in range(SAFFRON)] for i in range(BUSSES)]

MUSHROOMS = 8
W_MUSHROOMS = 1000
COOL_TRUCKS = 3
M = [[Bool(f"m_{i}_{j}") for j in range(MUSHROOMS)] for i in range(COOL_TRUCKS)]

GOATS = 10
W_GOATS = 2500
G = [[Bool(f"g_{i}_{j}") for j in range(GOATS)] for i in range(BUSSES)]

PEARS = 20
W_PEARS = 400
P = [[Bool(f"p_{i}_{j}") for j in range(PEARS)] for i in range(BUSSES)]

W_APPLES = 400
A = [Int(f"a_{i}") for i in range(BUSSES)]

def smaller_pairs(n, m):
    return [(i, k) for i in range(m) for k in range(m) if n <= i < k < m]

def saffron_sum(i):
    """Get the summed weight of saffron for truck i."""
    return Sum([S[i][j] * W_SAFFRON for j in range(SAFFRON)])

def mushroom_sum(i):
    """Get the summed weight of mushroom for truck i."""
    return Sum([M[i][j] * W_MUSHROOMS for j in range(MUSHROOMS)]) if i < 3 else 0

def goat_sum(i):
    """Get the summed weight of mushroom for truck i."""
    return Sum([G[i][j] * W_GOATS for j in range(GOATS)])

def pear_sum(i):
    """Get the summed weight of mushroom for truck i."""
    return Sum([P[i][j] * W_PEARS for j in range(GOATS)])


all_saffron_in_at_least_one_bus = [Or([S[i][j] for i in range(BUSSES)]) for j in range(SAFFRON)]
no_one_saffron_in_two_busses = [
    And([
        Or([Not(S[i][j]), Not(S[k][j])]) 
    for (i,k) in smaller_pairs(0,8)]) 
for j in range(SAFFRON)]

all_mushrooms_in_at_least_one_bus = [Or([M[i][j] for i in range(3)]) for j in range(BUSSES)]
no_one_mushroom_in_two_busses = [
    And([
        Or([Not(M[i][j]), Not(M[k][j])]) 
    for (i,k) in smaller_pairs(0,3)])e
for j in range(MUSHROOMS)]

all_goats_in_at_least_one_bus = [Or([G[i][j] for i in range(BUSSES)]) for j in range(GOATS)]
no_one_goat_in_two_busses = [
    And([
        Or([Not(G[i][j]), Not(G[k][j])]) 
    for (i,k) in smaller_pairs(0,8)]) 
for j in range(GOATS)]

all_pears_in_at_least_one_bus = [Or([P[i][j] for i in range(BUSSES)]) for j in range(PEARS)]
no_one_pear_in_two_busses = [
    And([
        Or([Not(P[i][j]), Not(P[k][j])]) 
    for (i,k) in smaller_pairs(0,8)]) 
for j in range(PEARS)]


at_most_one_saffron_in_a_bus = [
    And([
        Or([Not(S[i][k]), Not(S[i][j])]) 
    for (k,j) in smaller_pairs(0,4)]) 
for i in range(BUSSES)]


no_truck_weight_exceeded = [
    And(Sum(saffron_sum(i), mushroom_sum(i), goat_sum(i), pear_sum(i), A[i]*W_APPLES) <= W_BUS, A[i] >= 0)
for i in range(BUSSES)]


minimum_amount_of_apples = [Sum([A[i] for i in range(BUSSES)]) > 59]

phi = all_saffron_in_at_least_one_bus + no_one_saffron_in_two_busses + all_mushrooms_in_at_least_one_bus + no_one_mushroom_in_two_busses + all_goats_in_at_least_one_bus + no_one_goat_in_two_busses + all_pears_in_at_least_one_bus + no_one_pear_in_two_busses + no_truck_weight_exceeded + at_most_one_saffron_in_a_bus + minimum_amount_of_apples
#print(phi)

s = Solver()
s.add(phi)
s.check()
m = s.model()
total_apples = Sum([m.evaluate(A[i]) for i in range(BUSSES)])
print(total_apples)

#solve(phi)