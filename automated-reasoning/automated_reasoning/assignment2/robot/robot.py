ACTIONS = ["N", "S", "W", "E", "STAND_STILL"]

import math
import sys
from grid import Cell, Grid, SolutionChecker

from z3 import *

#############
# Task 3
#############

def solve(grid: Grid) -> tuple[int, dict[Cell, str]]:
    """
    A solution is a tuple (nr_steps, policy) where the nr_steps is the number of steps actually necessary,
    and a policy, which is a dictionary from grid cells to directions. Returning a policy is optional, but helpful for debugging.

    :return: a solution as described above
    """
    V_PLAN = {c:Int(f"p_{c}") for c in grid.colors}
    F_PLAN_BOUND = [Or(V_PLAN[c] == 1, V_PLAN[c] == 2, V_PLAN[c] == 3, V_PLAN[c] == 4)
                    for c in grid.colors if c != 1] + [V_PLAN[1] == 5]

    phi = F_PLAN_BOUND
  
    V_ALL_VARS = V_PLAN
  
    s = Solver()
    s.add(phi)
    s.check()
    try:
        m = s.model()
        plan = {c: int(str(m.evaluate(V_PLAN[c]))) for c in V_PLAN}
        policy = {cell: ACTIONS[plan[grid.get_color(cell)]-1] for cell in grid.cells}
        return 10, policy
    except:
        step_bound = 0
        policy = None
        return step_bound, policy
        return step_bound, policy
    

    # Short demonstration how to use the grid class.
    # Loop through all cells:
    # for cell in grid.cells:
    #     print(cell)
    #     # Is cell sticky?
    #     print("Cell sticky:", grid.is_sticky(cell))
    #     # Get neighbors of cell to all directions
    #     for direction in ACTIONS:
    #         print("Neighbor", direction, grid.neighbours(cell, direction))
    # step_bound is an int, policy is a dict from Cell to ACTIONS

# Tip: to run all experiments, execute
# ls *.csv | xargs -I {} python robot.py {}
def main():
    if len(sys.argv) != 2:
        print("Please provide exactly one argument (the csv file.)")
        return

    print(f"Loading a grid from file {sys.argv[1]}...")
    grid = Grid.from_csv(sys.argv[1])
    print(f"...The grid has dimensions {grid.xdim}x{grid.ydim}")
    print(f"...A trivial lower bound on the solution is {grid.lower_bound_on_solution}")
    print("Computing optimal number of steps!")
    nr_steps, policy = solve(grid)
    if policy is not None:
        solution_checker = SolutionChecker(grid, policy)
        try:
            print(solution_checker.run())
            print(f"Found a solution with {nr_steps} steps.")
        except:
            print("Solution checker failed.")
        grid.plot(
            f"test_solution.png", policy=policy, count=nr_steps
        )
    else:
        print("Found no solution.")

# If this file is running as a script, call the main method.
if __name__ == "__main__":
    main()
