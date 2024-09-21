from z3 import *

BUSSES = 8
CAP_BUS = 8000

S = [Int(f"s_{i}")for i in range(BUSSES)]
COOL_BUSSES = 3
M = [Int(f"m_{i}")for i in range(BUSSES)]
G = [Int(f"g_{i}")for i in range(BUSSES)]
P = [Int(f"p_{i}")for i in range(BUSSES)]
A = [Int(f"a_{i}") for i in range(BUSSES)]

four_saffron = [And(Sum([S[i] for i in range(BUSSES)]) == 4, And([S[i] >= 0 for i in range(BUSSES)]))]
eight_mushroom = [And(Sum([M[i] for i in range(COOL_BUSSES)]) == 8, And([M[i] >= 0 for i in range(BUSSES)]))]
ten_goat = [And(Sum([G[i] for i in range(BUSSES)]) == 10, And([G[i] >= 0 for i in range(BUSSES)]))]
twenty_pears = [And(Sum([P[i] for i in range(BUSSES)]) == 20, And([P[i] >= 0 for i in range(BUSSES)]))]

#for apples we only have to specify that there are at least 0
apples = [A[i] >= 0 for i in range(BUSSES)]

most_one_saffron = [And([S[i] <= 1 for i in range(BUSSES)])]

no_truck_weight_exceeded = [
    And(Sum(S[i]*700, M[i]*1000, G[i]*2500, P[i]*400, A[i]*400) <= CAP_BUS)
for i in range(BUSSES)]

truck_at_most_ten_units = [Sum(S[i], M[i], G[i], P[i], A[i]) <= 10 for i in range(BUSSES)]

minimum_amount_of_apples = [Sum([A[i] for i in range(BUSSES)]) > 35]

#for part 2:
no_goats_in_same_truck_as_apples = [Not(And(G[i] > 0, A[i] > 0)) for i in range(BUSSES)]

phi = four_saffron + eight_mushroom + ten_goat + twenty_pears + apples + most_one_saffron + no_truck_weight_exceeded + minimum_amount_of_apples + truck_at_most_ten_units# + no_goats_in_same_truck_as_apples
solve(phi)
s = Solver()
s.add(phi)
s.check()
m = s.model()
total_apples = Sum([m.evaluate(A[i]) for i in range(BUSSES)])
print(total_apples)

#answer part 1: 36 apples 0 + 6 + 6 + 8 + 0 + 4 + 8 + 4
#answer part 2: 25 apples 0 + 5 + 0 + 0 + 0 + 0 + 10 + 10
