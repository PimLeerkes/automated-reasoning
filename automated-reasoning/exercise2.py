from z3 import *
from itertools import product
from io import StringIO 
import sys

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

def flatten(xss):
    return [x for xs in xss for x in xs]

REGULAR_COMPONENTS_TUPLES = [
    (4, 5),
    (4, 6),
    (5, 20),
    (6, 9),
    (6, 10),
    (6,11),
    (7,8),
    (7,12),
    (10,10),
    (10,20)
]
POWER_COMPONENTS_TUPLES = [
    (4,3),
    (4,3)
]

COMPONENTS_TUPLES = REGULAR_COMPONENTS_TUPLES + POWER_COMPONENTS_TUPLES

# The sizes of the ten regular components are 4 × 5, 4 × 6, 5 × 20, 6 × 9, 6 × 10, 6 × 11,
# 7 × 8, 7 × 12, 10 × 10, 10 × 20, respectively.
regular_components = [[Int(f"cp_{i}_{s[0]}*{s[1]}_x"), 
                       Int(f"cp_{i}_{s[0]}*{s[1]}_y"),
                       Int(f"cp_{i}_{s[0]}*{s[1]}_w"),
                       Int(f"cp_{i}_{s[0]}*{s[1]}_h"),
                       ] for (i,s) in enumerate(REGULAR_COMPONENTS_TUPLES)]

power_components = [[Int(f"po_{i}_{s[0]}*{s[1]}_x"), 
                       Int(f"po_{i}_{s[0]}*{s[1]}_y"),
                       Int(f"po_{i}_{s[0]}*{s[1]}_w"),
                       Int(f"po_{i}_{s[0]}*{s[1]}_h"),
] for (i,s) in enumerate(POWER_COMPONENTS_TUPLES)]

components = regular_components + power_components

components_sizes = [
    [Or(
        [ # s(x, y, w, h) and c(w, h)
            And(s[2] == c[0], s[3] == c[1]),
            And(s[2] == c[1], s[3] == c[0])
        ]
    )]
for (s,c) in zip(components, COMPONENTS_TUPLES)]

WIDTH = 30
HEIGHT = 30
all_components_in_bound = [And([c[0] + w <= WIDTH, c[1] + h <= HEIGHT, c[0] >= 0, c[1] >= 0]) for (c,(w,h)) in zip(components, COMPONENTS_TUPLES)]

# Every square on the chip has a int variable that is set to the component number that uses it, unbound is empty.

# squares[x][y]
squares = [[Int(f"sq_{x}*{y}") for y in range(HEIGHT)] for x in range(WIDTH)]

# Now just enforce using squares
def claim_space(x, y, w, h, c_no):
    try:
        return And([squares[x_][y_] == c_no for (x_, y_) in product(range(x, x+w), range(y, y+h))])
    except IndexError:
        return And([])

def get_w(c_no):
    return COMPONENTS_TUPLES[c_no][0]

def get_h(c_no):
    return COMPONENTS_TUPLES[c_no][1]

def enforce_component(c_no):
    comp = components[c_no]
    return [
        Implies(And(comp[0] == x, comp[1] == y), claim_space(x, y, get_w(c_no), get_h(c_no), c_no))
    for (x,y) in product(range(WIDTH), range(HEIGHT))]

def no_overlap():
    res = []
    for c_no in range(len(COMPONENTS_TUPLES)):
        print(c_no)
        res.append(enforce_component(c_no))
    return flatten(res)

def sq_string_to_coords(s):
    tail = str(s)[3:]
    strx, stry = tail.split("*")
    x = int(strx)
    y = int(stry)
    return (x, y)

def get_assignment():
    set_option(max_args=10000)
    s: Solver = Solver()
    print("Solving")
    nov = no_overlap()
    #print(nov[0])

    flat_squares = flatten(squares)
    s.add(flatten(components_sizes) + all_components_in_bound + nov)
    s.check()
    m = s.model()
    results = [m.evaluate(var) for var in flat_squares]
    return [(sq_string_to_coords(sq), res) for (sq, res) in zip(flat_squares, results)]
    # m = s.model()
    # print(len(m))
    # for n in m:
    #     print(n)

board = [["." for y in range(HEIGHT)] for x in range(WIDTH)]
solution = get_assignment()

for ((x,y), v) in solution:
    board[y][x] = v

for row in board:
    print(' '.join(map(str, row)))
#print(capture_solve_filter())

#print(claim_space(29, 0, 5, 6, 77))

# chip_width = Int("width")
# chip_height = Int("height")

# # pc = power component
# pc_width = Int("pc_width")
# pc_height = Int("pc_height")
