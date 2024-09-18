from z3 import *

def solve_and_print(P, R_a, R_b, PR, all_vars=False, pretty=True, print_phi=False):
    phi = P + R_a + R_b
    s = Solver()
    print("Solving")
    s.check()
    m = s.model()
    results = {var: m.evaluate(var) for var in phi}
    if all_vars:
        print(results)
    if pretty:
        print("===\nHOUSES and COUPLES")
        for r_no in range(5):
            out = f"House {r_no}: "
            for p in P:
                val = results[p]
                if val == r_no:
                    out += f" {p}"
            print(out)

        for r_no, (r_a, r_b) in enumerate(zip(R_a, R_b)):
            house_a = results[r_a]
            house_b = results[r_b]
            print("======")
            print(f"ROUND: {r_no}")
            print(f"House a: {house_a}")
            print(f"House b: {house_b}")
            print("PEOPLE")

            a = []
            b = []
            unbound = []
            for p_no in range(10):
                key = f"p_{p_no}_{r_no}"
                house_of_p = results[key]
                if house_of_p == 0:
                    a.append(p_no)
                elif house_of_p == 1:
                    b.append(p_no)
                else:
                    unbound.append(p_no)

            print(f"A: {a}")
            print(f"B: {b}")
            print(f"unbound: {unbound}")

            
    