"""This file defines the Cell and Grid classes for the robot exercise."""
import csv
START_CELL_OBS = 0
TARGET_CELL_OBS = 1
LAVA_CELL_OBS = 2
STICKY_CELL_OBS = 4

class Cell:
    """
    Individual cells in a grid, a basic container for (x,y) tuples with very limited operations.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"<{self.x}, {self.y}>"

    def __hash__(self):
        return hash(self.x) ^ hash(self.y)

    def distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Grid:
    """
    This grid contains a list of all the cells and their types.
    It contains a series of convenience functions, including reading and writing to files,
    generating random grids, plotting grids, and computing which cells are the neighbours of a particular cell.
    """

    def __init__(self, grid):
        """
        Internal initialization method for grid class. Requires a 2d matrix with the grid. Do not use.

        :param grid: A 2d matrix of Cells.
        """
        self._grid = grid
        self._colors = set()
        for row in grid:
            for entry in row:
                self._colors.add(entry)
        self._cells = []
        for x in range(0, self.xdim):
            for y in range(0, self.ydim):
                self._cells.append(Cell(x, y))

    @classmethod
    def from_csv(cls, path):
        """
        Creates a grid from a CSV file.

        :param path:
        :return:
        """
        grid = []
        with open(path, encoding="utf-8") as csvfile:
            tablereader = csv.reader(csvfile, delimiter=",", quotechar="|")
            for row in tablereader:
                grid.append([int(entry) for entry in row])
        return cls(grid)

    @property
    def colors(self):
        return self._colors

    @property
    def xdim(self):
        return len(self._grid)

    @property
    def ydim(self):
        return len(self._grid[0])

    @property
    def maxx(self):
        return self.xdim - 1

    @property
    def maxy(self):
        return self.ydim - 1

    @property
    def cells(self):
        return self._cells

    def initial_cells(self):
        """
        Returns the list of cells where the robot may start.
        """
        return [c for c in  self._cells if self.is_start(c)]

    def __str__(self):
        return "\n".join(
            [
                "\t".join([f"{self._grid[x][y]}" for y in range(0, self.ydim)])
                for x in range(0, self.ydim)
            ]
        )

    @property
    def lower_bound_on_solution(self):
        """
        Computes the shortest possible solution length.
        :return:
        """
        dist = 0
        for c in self.cells:
            if not self.is_start(c):
                continue
            dist = max(
                dist,
                min([c.distance(d) for d in self.cells if self.is_target(d)]),
            )
        return dist

    @property
    def upper_bound_on_solution(self):
        """
        Computes the longest possible solution length (not counting sticky).
        :return:
        """
        return (1 + self.maxx) * (1 + self.maxy)

    def get_movement_cost(self, cell):
        """
        Returns the cost of movement when starting in the given cell.
        """
        return 7 if self.is_sticky(cell) else 1

    def is_target(self, cell):
        return self.get_color(cell) == TARGET_CELL_OBS

    def is_lava(self, cell):
        return self.get_color(cell) == LAVA_CELL_OBS

    def is_start(self, cell):
        return self.get_color(cell) == START_CELL_OBS

    def is_sticky(self, cell):
        return self.get_color(cell) == STICKY_CELL_OBS

    def get_color(self, cell):
        """
        Return the color (i.e., the ground type) of a cell.
        """
        return self._grid[cell.x][cell.y]

    def neighbours(self, cell, dir):
        """
        Computes a list of neighbours of a given cell, when going in a particular direction.
        For most types of underground, every cell has a unique neighbour in every direction,
        in which case the resulting list has one entry.
        """
        assert dir in ["N", "S", "W", "E"]
        if dir == "N":
            return [Cell(max(cell.x - 1, 0), cell.y)]
        elif dir == "S":
            return [Cell(min(cell.x + 1, self.maxx), cell.y)]
        elif dir == "W":
            return [Cell(cell.x, max(cell.y - 1, 0))]
        elif dir == "E":
            return [Cell(cell.x, min(cell.y + 1, self.maxy))]

    def inv_neighbours(self, cell, dir):
        """
        Computes for a cell c and a direction d the inverse neighbours, i.e.,
         all the cells that reach the given cell by taking direction d.
        """
        assert dir in ["N", "S", "W", "E"]
        result = []
        if dir == "E" and cell.y > 0:
            result.append(Cell(cell.x, cell.y - 1))
        if dir == "W" and cell.y < self.maxy:
            result.append(Cell(cell.x, cell.y + 1))
        if dir == "S" and cell.x > 0:
            result.append(Cell(cell.x - 1, cell.y))
        if dir == "N" and cell.x < self.maxx:
            result.append(Cell(cell.x + 1, cell.y))
        return [n for n in result if not self.is_target(n)]

    def plot(self, path, policy=None, count=None):
        """
        This method requires MatPlotLib and NumPy and plots the grid.
        The internals of this method are not relevant for any exercises.

        :param path:
        :param policy:
        :param count:
        :return:
        """
        # Some color names for the different types of ground.
        COLOR_NAMES = [
            "green",
            "black",
            "crimson",
            "white",
            "white",
            "violet",
            "lightskyblue",
            "orange",
            "blue",
            "yellow",
            "deepskyblue",
            "teal",
            "navajowhite",
            "darkgoldenrod",
            "lightsalmon",
        ]

        DIR_TO_CARET = {"W": 4, "E": 5, "N": 6, "S": 7}

        # These imports are here to avoid this as mandatory imports.
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        import numpy as np

        def surface_to_text(surface):
            if surface == START_CELL_OBS:
                return "S"
            if surface == TARGET_CELL_OBS:
                return "T"
            if surface == LAVA_CELL_OBS:
                return "L"
            if surface == STICKY_CELL_OBS:
                return "D"
            return surface

        def dir_to_carret(dir):
            return DIR_TO_CARET[dir]

        def xdir_offset(dir):
            if dir == "W":
                return -0.6
            if dir == "E":
                return 0.6
            return 0.0

        def ydir_offset(dir):
            if dir == "N":
                return -0.6
            if dir == "S":
                return 0.6
            return 0.0

        fig = plt.figure()
        ax = fig.subplots()
        column_labels = list(range(0, self.ydim))
        ax.set_xlim([-0.4, self.maxx + 1.4])
        ax.set_ylim([-0.4, self.maxy + 1.4])
        row_labels = list(range(0, self.xdim))
        # put the major ticks at the middle of each cell
        ax.set_xticks(np.arange(self.xdim) + 0.5, minor=False)
        ax.set_yticks(np.arange(self.ydim) + 0.5, minor=False)

        # want a more natural, table-like display
        ax.invert_yaxis()
        ax.xaxis.tick_top()

        ax.set_xticklabels(row_labels, minor=False)
        ax.set_yticklabels(column_labels, minor=False)
        ax.set_xlabel("y")
        ax.set_ylabel("x")
        ax.set_aspect(1)
        if count is not None:
            ax.set_title(f"Solution for {count} steps")
        ax.pcolor(
            self._grid,
            cmap=mpl.colors.ListedColormap(COLOR_NAMES),
            edgecolors="k",
            linestyle="dashed",
            linewidths=0.2,
            vmin=0,
            vmax=len(COLOR_NAMES),
        )
        bid = dict(boxstyle="round", facecolor="white", alpha=0.7)

        for c in self.cells:
            if self.is_target(c):
                ax.scatter(c.y + 0.5, c.x + 0.5, s=320, marker="*", color="gold")
            elif self.is_lava(c):
                ax.scatter(c.y + 0.5, c.x + 0.5, s=320, marker="X", color="black")
            elif self.is_sticky(c):
                ax.scatter(c.y + 0.5, c.x + 0.5, s=320, marker="D", color="lightblue")
            elif self.is_start(c):
                ax.scatter(c.y + 0.5, c.x + 0.5, s=320, marker="*", color="lightgreen")
            else:
                ax.text(
                    c.y + 0.6,
                    c.x + 0.6,
                    surface_to_text(self._grid[c.x][c.y]),
                    fontsize=10,
                    verticalalignment="top",
                    bbox=bid,
                )
            if (
                policy is not None
                and c in policy
                and not self.is_target(c)
                and not self.is_lava(c)
            ):
                ax.scatter(
                    c.y + 0.5 + xdir_offset(policy.get(c)),
                    c.x + 0.5 + ydir_offset(policy.get(c)),
                    s=220,
                    marker=dir_to_carret(policy.get(c)),
                    color="black",
                )
        fig.savefig(path)
        plt.close(fig)

class SolutionChecker:
    """
    Small code to check the number of steps a policy requires.
    """
    def __init__(self, grid, policy):
        self._grid = grid
        self._policy = policy
        self._cache = dict()

    def _recursive_check(self, cell):
        """
        Helper function to compute the longest path.
        """
        if self._grid.is_target(cell):
            return 0
        if cell not in self._cache:
            self._cache[cell] = max([self._recursive_check(cell) for cell in self._grid.neighbours(cell, self._policy[cell] if cell in self._policy else None)]) + self._grid.get_movement_cost(cell)
            return self._cache[cell]
        return self._cache[cell]

    def run(self):
        """
        Returns the number of steps a policy requires.
        """
        return max([self._recursive_check(cell) for cell in self._grid.initial_cells()])