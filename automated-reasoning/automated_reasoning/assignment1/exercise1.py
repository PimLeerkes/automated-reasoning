from z3 import *

BUSSES = 8
CAP_BUS = 8000

S = [Int(f"s_{i}")for i in range(BUSSES)]
M = [Int(f"m_{i}")for i in range(BUSSES)]
G = [Int(f"g_{i}")for i in range(BUSSES)]
P = [Int(f"p_{i}")for i in range(BUSSES)]
A = [Int(f"a_{i}") for i in range(BUSSES)]

four_saffron = [And(Sum([S[i] for i in range(BUSSES)]) == 4, And([S[i] >= 0 for i in range(BUSSES)]))]
eight_mushroom = [And(Sum([M[i] for i in range(BUSSES)]) == 8, And([M[i] >= 0 for i in range(BUSSES)]))]
ten_goat = [And(Sum([G[i] for i in range(BUSSES)]) == 10, And([G[i] >= 0 for i in range(BUSSES)]))]
twenty_pears = [And(Sum([P[i] for i in range(BUSSES)]) == 20, And([P[i] >= 0 for i in range(BUSSES)]))]

#for apples we only have to specify that there are at least 0
apples = [A[i] >= 0 for i in range(BUSSES)]

most_one_saffron = [And([S[i] <= 1 for i in range(BUSSES)])]

mushrooms_cool_trucks = [M[i] == 0 for i in range(3,BUSSES)]

no_truck_weight_exceeded = [
    And(Sum(S[i]*700, M[i]*1000, G[i]*2500, P[i]*400, A[i]*400) <= CAP_BUS)
for i in range(BUSSES)]

truck_at_most_ten_units = [Sum(S[i], M[i], G[i], P[i], A[i]) <= 10 for i in range(BUSSES)]

#for part 2:
no_goats_in_same_truck_as_apples = [Not(And(G[i] > 0, A[i] > 0)) for i in range(BUSSES)]

phi = four_saffron + eight_mushroom + ten_goat + twenty_pears + apples + most_one_saffron + mushrooms_cool_trucks + no_truck_weight_exceeded + truck_at_most_ten_units + no_goats_in_same_truck_as_apples

#we optimize over the sum of apples
opt = Optimize()
opt.add(phi)
opt.maximize(Sum(A))

# If sat we print the table in latex format
if opt.check() == sat:
    m = opt.model()

    latex_table = "\\begin{tabular}{|c|" + "c|" * BUSSES + "}\n\\hline\n"

    latex_table += "Cargo Type"
    for i in range(BUSSES):
        latex_table += f" & Bus {i}"
    latex_table += " \\\\\n\\hline\n"

    latex_table += "Saffron  "
    for i in range(BUSSES):
        latex_table += f" & {m.evaluate(S[i])}"
    latex_table += " \\\\\n"
    
    latex_table += "Mushroom "
    for i in range(BUSSES):
        latex_table += f" & {m.evaluate(M[i])}"
    latex_table += " \\\\\n"
    
    latex_table += "Goat     "
    for i in range(BUSSES):
        latex_table += f" & {m.evaluate(G[i])}"
    latex_table += " \\\\\n"
    
    latex_table += "Pears    "
    for i in range(BUSSES):
        latex_table += f" & {m.evaluate(P[i])}"
    latex_table += " \\\\\n"
    
    latex_table += "Apples   "
    for i in range(BUSSES):
        latex_table += f" & {m.evaluate(A[i])}"
    latex_table += " \\\\\n\\hline\n"

    latex_table += "\\end{tabular}"

    print(latex_table)

else:
    print("No solution")


