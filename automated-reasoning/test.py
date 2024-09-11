from z3 import *

BUSSES = 8
WEIGHT_LIMIT = 8000

# Create variables i = bus
B = [Int(f"b_{i}") for i in range(BUSSES)]

SAFFRON = 4
S = [[Bool(f"s_{i}_{j}") for j in range(SAFFRON)] for i in range(BUSSES)]

MUSHROOMS = 8
COOL_TRUCKS = 3
M = [[Bool(f"m_{i}_{j}") for j in range(MUSHROOMS)] for i in range(COOL_TRUCKS)]

GOATS = 10
G = [[Bool(f"g_{i}_{j}") for j in range(GOATS)] for i in range(BUSSES)]

PEARS = 20
P = [[Bool(f"p_{i}_{j}") for j in range(PEARS)] for i in range(BUSSES)]
bus_weight_limit = [B[i] <= WEIGHT_LIMIT for i in range(BUSSES)]

def smaller_pairs(n, m):
    return [(i, k) for i in range(m) for k in range(m) if n <= i < k < m]

all_saffron_in_at_least_one_bus = [Or([S[i][j] for i in range(BUSSES)]) for j in range(SAFFRON)]
max_one_saffron_per_bus = [
    And([
        Or([Not(S[i][j]), Not(S[k][j])]) 
    for (i,k) in smaller_pairs(0,8)]) 
for j in range(SAFFRON)]

#max_one_saffron_per_bus = [And(Or(Not(s[i][0]),s[][]),s[i][1],s[i][2],s[i][3]) for i in range(BUSSES)]


#saffron_max_one_bus = [And([Or(Not(Si][j])m,Not(S[k][j])) for j in range(BUSSES) if 0 < i < k <= 8]) for i in range SAFFRON]

mushrooms_in_cool_trucks = []


mushrooms = [Or([M[i][j] for i in range(3)]) for j in range(BUSSES)]
goats = [Or([G[i][j] for i in range(BUSSES)]) for j in range(GOATS)]
pears = [Or([P[i][j] for i in range(BUSSES)]) for j in range(PEARS)]


final_condition = [B[i] <= 8000 and B[i] = total_s
    
#[And(B[i] <= 8000], B[i] == Sum(Sum([S[i][j]*700 for j in range(SAFFRON)]),Sum([M[i][j]*1000 for j in range(MUSHROOMS)]),Sum([G[i][j]*2500 for j in range(GOATS)]),Sum([P[i][j]*400 for j in range(PEARS)])))for i in range(BUSSES)]

phi = bus_weight_limit + all_saffron_in_a_bus + mushrooms + goats + pears + total_sum
solve(phi)
