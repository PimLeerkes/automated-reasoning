ACTIONS = ["N", "S", "W", "E", "STAND_STILL"]

import math
import sys
from grid import Cell, Grid, SolutionChecker, START_CELL_OBS, TARGET_CELL_OBS, LAVA_CELL_OBS, STICKY_CELL_OBS

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

    best_t = 0
    best_policy = None
    for T in reversed(range(3)):
        V_PLAN = {c:Int(f"p_{c}") for c in grid.colors}
        F_PLAN_BOUND = [Or(V_PLAN[c] == 1, V_PLAN[c] == 2, V_PLAN[c] == 3, V_PLAN[c] == 4)
                        for c in grid.colors if c != 1] + [V_PLAN[1] == 5]
        NO_INITIAL_CELLS = len(grid.initial_cells())
        V_X = [[Int(f"x_{s}_{t}") for t in range(T+1)] 
        for s in range(NO_INITIAL_CELLS)]
        V_Y = [[Int(f"y_{s}_{t}") for t in range(T+1)] 
        for s in range(NO_INITIAL_CELLS)]

        # Warning, the directions are all weird and messed up.
        def neighbors_id(x, y, d):
            return grid.neighbours(grid.get_cell_at(x,y), ACTIONS[d])[0]

        # print(neighbors_id(3,3,0))
        # quit()

        def match(s, t, c, x, y) -> list | None:
            """Return a formula that is true iff in scenario s:
                the position of the robot is (x,y) at time t, and the color of (x,y) is c."""
            V_X[s][t] == x
            return And([V_X[s][t] == x, V_Y[s][t] == y]) if grid.get_color(grid.get_cell_at(x,y)) == c else None

        # In the formalization, we account for falling off the map, but the grid class already does that for us.
        F_BASIC_MOVEMENT = [
            [
                Implies(
                    V_PLAN[c] == d
                , # ===>
                    And(V_X[s][t] == neighbors_id(x, y, d).x, V_Y[s][t] == neighbors_id(x, y, d).y)
                )
            ]
            for d in range(len(ACTIONS))
            for y in range(grid.ydim)
            for x in range(grid.xdim)
            for c in grid.colors
            for t in range(T-1)
            for s in range(NO_INITIAL_CELLS) 
            if match(s,t,c,x,y) != None and\
            c != LAVA_CELL_OBS and c != STICKY_CELL_OBS]
        # print(F_BASIC_MOVEMENT[:10])
        # print(len(F_BASIC_MOVEMENT))
        # quit()

        phi = F_PLAN_BOUND
    
        s = Solver()
        s.add(phi)
        s.check()
        try:
            m = s.model()
            plan = {c: int(str(m.evaluate(V_PLAN[c]))) for c in V_PLAN}
            policy = {cell: ACTIONS[plan[grid.get_color(cell)]-1] for cell in grid.cells}
            best_t = T
            best_policy = policy
            print(f"Found better solution with T={T}")
        except:
            print("Previous solution was best.")
            return best_t, best_policy
    print("Warning, out of the loop!")
    return best_t, best_policy

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
