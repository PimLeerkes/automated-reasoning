from z3 import *

BUSSES = 8
SAFFRON = 4
S = [[Bool(f"s_{i}_{j}") for j in range(SAFFRON)] for i in range(BUSSES)]

def smaller_pairs(n, m):
    return [(i, k) for i in range(m) for k in range(m) if n <= i < k < m]

correct_amount_of_saffron = [
    And([
        Or([Not(S[i][j]), Not(S[k][j])]) 
    for (i,k) in smaller_pairs(0,8)]) 
for j in range(SAFFRON)]

# correct_amount_of_saffron = [Or([
#     And([
#         Or([And(Not(S[i][j]), Not(S[k][j]))]) for (i, k) in smaller_pairs(0, 8)
#     ])
# ]) for j in range(SAFFRON)]

print(smaller_pairs(0,8))
print(correct_amount_of_saffron)