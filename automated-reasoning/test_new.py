from z3 import *

l = [Sum(Int('a') == Int('b') + Int('a') == Int('b')) == 0]
print(l)
solve(l)