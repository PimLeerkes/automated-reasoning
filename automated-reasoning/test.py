from z3 import *

NO_BUSSES = 8
WEIGHT_LIMIT = 8000

# Create variables i = bus
B = [Int(f"b_{i}") for i in range(NO_BUSSES)]
S = [Bool(f"s_{i}{j}") for j in range(4) for i in range(8)]
# M = [Bool(f"m_{i}{j}") for j in range(8) for i in range(3)]
# G = [Bool(f"g_{i}{j}") for j in range(10) for i in range(8)]
# P = [Bool(f"p_{i}{j}") for j in range(20) for i in range(8)]
bus_weight_limit = [B[i] <= WEIGHT_LIMIT for i in range(NO_BUSSES)]
bus_weight_limit += S

phi = bus_weight_limit
solve(phi)
# x = Int('x')
# y = Int('y')
# solve(x > 2, y < 10, x + 2*y == 7)