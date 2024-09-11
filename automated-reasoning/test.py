from z3 import *

BUSSES = 8
W_BUS = 8000

# Create variables i = bus
#B = [Int(f"b_{i}") for i in range(BUSSES)]

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
#bus_weight_limit = [B[i] <= W_BUS for i in range(BUSSES)]

W_APPLES = 400

def smaller_pairs(n, m):
    return [(i, k) for i in range(m) for k in range(m) if n <= i < k < m]

def saffron_sum(i, max_weight, amount):
    """Get the summed weight of saffron for truck i."""
    return Sum([S[i][j] * W_SAFFRON for j in range(SAFFRON)])

def mushroom_sum(i):
    """Get the summed weight of mushroom for truck i."""
    return Sum([S[i][j] * W_MUSHROOMS for j in range(MUSHROOMS)])

def goat_sum(i):
    """Get the summed weight of mushroom for truck i."""
    return Sum([S[i][j] * W_GOATS for j in range(GOATS)])

def pear_sum(i):
    """Get the summed weight of mushroom for truck i."""
    return Sum([S[i][j] * W_PEARS for j in range(GOATS)])

mushrooms = [Or([M[i][j] for i in range(3)]) for j in range(BUSSES)]
goats = [Or([G[i][j] for i in range(BUSSES)]) for j in range(GOATS)]
pears = [Or([P[i][j] for i in range(BUSSES)]) for j in range(PEARS)]

all_saffron_in_at_least_one_bus = [Or([S[i][j] for i in range(BUSSES)]) for j in range(SAFFRON)]
no_two_busses_have_the_same_saffron = [
    And([
        Or([Not(S[i][j]), Not(S[k][j])]) 
    for (i,k) in smaller_pairs(0,8)]) 
for j in range(SAFFRON)]

no_truck_weight_exceeded = [
    Sum([saffron_sum(i), mushroom_sum(i), goat_sum(i), pear_sum(i)]) <= W_BUS
for i in range(BUSSES)]

#max_one_saffron_per_bus = [And(Or(Not(s[i][0]),s[][]),s[i][1],s[i][2],s[i][3]) for i in range(BUSSES)]
#saffron_max_one_bus = [And([Or(Not(Si][j])m,Not(S[k][j])) for j in range(BUSSES) if 0 < i < k <= 8]) for i in range SAFFRON]
#[And(B[i] <= 8000], B[i] == Sum(Sum([S[i][j]*700 for j in range(SAFFRON)]),Sum([M[i][j]*1000 for j in range(MUSHROOMS)]),Sum([G[i][j]*2500 for j in range(GOATS)]),Sum([P[i][j]*400 for j in range(PEARS)])))for i in range(BUSSES)]

phi = 
print(phi)
solve(phi)
