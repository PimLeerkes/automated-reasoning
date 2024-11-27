ACTIONS = ["N", "S", "W", "E", "STAND_STILL"]

import math
import sys
import itertools
from grid import Cell, Grid, SolutionChecker, START_CELL_OBS, TARGET_CELL_OBS, LAVA_CELL_OBS, STICKY_CELL_OBS

from z3 import *

def flatten(l:list):
    return list(itertools.chain(*l))

#############
# Task 3
#############

def solve(grid: Grid) -> tuple[int, dict[Cell, str]]:
    """
    A solution is a tuple (nr_steps, policy) where the nr_steps is the number of steps actually necessary,
    and a policy, which is a dictionary from grid cells to directions. Returning a policy is optional, but helpful for debugging.

    :return: a solution as described above
    """
    for T in range(grid.lower_bound_on_solution,9999999):
    #for T in range(13,9999999):
        V_PLAN = {c:Int(f"p_{c}") for c in grid.colors}
        F_PLAN_BOUND = [Or(V_PLAN[c] == 1, V_PLAN[c] == 2, V_PLAN[c] == 3, V_PLAN[c] == 4)
                        for c in grid.colors if c != 1] + [V_PLAN[1] == 5]
        NO_INITIAL_CELLS = len(grid.initial_cells())
        V_X = [[Int(f"x_{s}_{t}") for t in range(T)] 
        for s in range(NO_INITIAL_CELLS)]
        V_Y = [[Int(f"y_{s}_{t}") for t in range(T)] 
        for s in range(NO_INITIAL_CELLS)]
        F_X_BOUNDS = [And(V_X[s][t] >= 0, V_X[s][t] < grid.xdim) for t in range(T) for s in range(NO_INITIAL_CELLS)]
        F_Y_BOUNDS = [And(V_Y[s][t] >= 0, V_Y[s][t] < grid.ydim) for t in range(T) for s in range(NO_INITIAL_CELLS)]

        # Warning, the directions are all weird and messed up.
        def neighbors_id(x, y, d):
            return grid.neighbours(grid.get_cell_at(x,y), ACTIONS[d-1])[0]
        
        def get_color_id(x,y):
            return grid.get_color(grid.get_cell_at(x,y))

        # print(neighbors_id(0,0,4))
        # quit()

        def match(s, t, c, x, y) -> list | None:
            """Return a formula that is true iff in scenario s:
                the position of the robot is (x,y) at time t, and the color of (x,y) is c."""
            return And([V_X[s][t] == x, V_Y[s][t] == y]) if get_color_id(x,y) == c else None

        # In the formalization, we account for falling off the map, but the grid class already does that for us.
        F_BASIC_MOVEMENT = [
            
            Implies(
                And(V_PLAN[c] == d, match(s,t,c,x,y))
            , # ===>
                And(V_X[s][t+1] == neighbors_id(x, y, d).x, V_Y[s][t+1] == neighbors_id(x, y, d).y)
            )
            
            for d in range(len(ACTIONS))
            for y in range(grid.ydim)
            for x in range(grid.xdim)
            for c in grid.colors
            for t in range(T-1)
            for s in range(NO_INITIAL_CELLS) 
            if match(s,t,c,x,y) != None and\
            c != LAVA_CELL_OBS and c != STICKY_CELL_OBS
        ]
        
        F_STANDING_STILL = [
            Implies(
                And(V_PLAN[c] == 5, match(s,t,c,x,y))
            , # ===>
                And(V_X[s][t+1] == V_X[s][t], V_Y[s][t+1] == V_Y[s][t])
            )
            for y in range(grid.ydim)
            for x in range(grid.xdim)
            for c in grid.colors
            for t in range(T-1)
            for s in range(NO_INITIAL_CELLS) 
            if match(s,t,c,x,y) != None and\
            c != LAVA_CELL_OBS and c != STICKY_CELL_OBS
        ]
        # print(F_BASIC_MOVEMENT[:10])
        # print(len(F_BASIC_MOVEMENT))
        # quit()
        # [print(m) for m in F_BASIC_MOVEMENT[0:50]]
        # print(len(F_BASIC_MOVEMENT))

        F_LAVA_TILES = [
            Not(match(s,t,LAVA_CELL_OBS,x,y))
            for y in range(grid.ydim)
            for x in range(grid.xdim)
            for t in range(T-1)
            for s in range(NO_INITIAL_CELLS)
            if match(s,t,LAVA_CELL_OBS,x,y) != None
        ]

        F_STICKY_TILES = [
            Implies(match(s,t,STICKY_CELL_OBS,x,y),
                Implies(Or(V_X[s][t-1] != V_X[s][t], V_Y[s][t-1] != V_Y[s][t]),
                    And([And(V_X[s][t] == V_X[s][tt], V_Y[s][t] == V_Y[s][tt])
                        for tt in range(t+1, min(t+6,T))
                    ] + [Implies(V_PLAN[STICKY_CELL_OBS] == d,
                        And(V_X[s][t+6] == neighbors_id(x,y,d).x, V_Y[s][t+6] == neighbors_id(x,y,d).y,
                            Or(V_X[s][t+6] != V_X[s][t], V_Y[s][t+6] != V_Y[s][t])))
                        for d in range(len(ACTIONS)) if t+6 < T])
                ))
            for y in range(grid.ydim)
            for x in range(grid.xdim)
            for t in range(T-1)
            for s in range(NO_INITIAL_CELLS)
            if match(s,t,STICKY_CELL_OBS,x,y) != None
        ]

        F_START = [
            And(V_X[s][0] == grid.get_cell_at(ic.x, ic.y).x, V_Y[s][0] == grid.get_cell_at(ic.x, ic.y).y)
            for (s, ic) in zip(range(NO_INITIAL_CELLS), grid.initial_cells())
        ]
        #print(F_START)

        F_FINISH = [
            Implies(And(V_X[s][T-1] == x, V_Y[s][T-1] == y)
            , # ===>
                get_color_id(x,y) == TARGET_CELL_OBS)

            for y in range(grid.ydim)
            for x in range(grid.xdim)
            for s in range(NO_INITIAL_CELLS) 
        ]

        phi = F_PLAN_BOUND + F_X_BOUNDS + F_Y_BOUNDS + F_BASIC_MOVEMENT + F_STANDING_STILL + F_START + F_FINISH + F_LAVA_TILES + F_STICKY_TILES
        #phi = F_FINISH
    
        s = Solver()
        s.add(phi)
        if s.check() == sat:
            m = s.model()
            plan = {c: int(str(m.evaluate(V_PLAN[c]))) for c in V_PLAN}
            action_plan = {c: ACTIONS[p-1] for c,p in plan.items()}
            policy = {cell: action_plan[grid.get_color(cell)] for cell in grid.cells}

            DEBUG = False
            if DEBUG:
                print(action_plan)
                print("T:", T)
                for s in range(NO_INITIAL_CELLS):
                    print(f"PATH {s}:")
                    for t in range(T):
                        x = int(str(m.evaluate(V_X[s][t])))
                        y = int(str(m.evaluate(V_Y[s][t])))
                        d = plan[get_color_id(x,y)]
                        print("t:", t, f"({x},{y}) color: ", get_color_id(x,y), "plan:", action_plan[get_color_id(x,y)], "planned neighbor:", neighbors_id(x,y,d))

            print(f"Success in {T}")
            return T, policy
        
        else:
            print(f"Failed with {T} steps, next iteration.")
    print("Warning, out of the loop!")

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
            sol_steps = solution_checker.run()
            if sol_steps == nr_steps:
                print(f"Solution checker verified a solution with {nr_steps} steps.")
            else:
                print(f"Mismatch! The solution checker found {sol_steps} but find_solution gives {nr_steps}.")
        except:
            print("Solution checker failed.")
        grid.plot(
            sys.argv[1] + ".png", policy=policy, count=nr_steps
        )
    else:
        print("Found no solution.")

# If this file is running as a script, call the main method.
if __name__ == "__main__":
    main()
