from z3 import *

def solve_and_print(P, R_a, R_b, all_vars=False, pretty=True):
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
        for i in range(5):
            out = "House {i}: "
            for p in P:
                val = results[p]
                if val == i:
                    out += f" {p}"
            print(out)

        for i, (r_a, r_b) in enumerate(zip(R_a, R_b)):
            print("======")
            print(f"ROUND: {i}")
            print(f"House a: {results(r_a)}")
            print(f"House b: {results(r_b)}")
            print("People: TODO")
    