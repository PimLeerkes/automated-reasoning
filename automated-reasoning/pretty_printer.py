from z3 import *

def flatten(xss):
    return [x for xs in xss for x in xs]

def get_hosts(h_no, P, results):
    res = []
    for p in P:
        val = results[p]
        if val == h_no:
            res.append(p)
    return res

def solve_and_print(P, R_a, R_b, PR, phi, all_vars=False, pretty=True):
    s = Solver()
    print("Solving")
    s.add(phi)
    s.check()
    m = s.model()
    results = {var: m.evaluate(var) for var in (P + R_a + R_b + flatten(PR))}
    if all_vars:
        print(results)
    if pretty:
        print("=====\nHOUSES and COUPLES")
        for h_no in range(5):
            print(f"House {h_no}: {get_hosts(h_no, P, results)}")
        print()

        for r_no, (r_a, r_b) in enumerate(zip(R_a, R_b)):
            house_a = results[r_a]
            house_b = results[r_b]
            a = []
            b = []
            unbound = []
            for p_no in range(10):
                key = PR[r_no][p_no]
                house_of_p = results[key]
                if house_of_p == 0:
                    a.append(p_no)
                elif house_of_p == 1:
                    b.append(p_no)
                else:
                    unbound.append(p_no)
            print("======")
            print(f"ROUND: {r_no}")
            print(f"Hosts A: {get_hosts(house_a, P, results)} of house {house_a}")
            print(f"People A: {a}")
            print(f"Hosts B: {get_hosts(house_b, P, results)} of house {house_b}")
            print(f"People B: {b}")
            print(f"unbound: {unbound}\n")

            
    