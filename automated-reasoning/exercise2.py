from z3 import *
from itertools import product
from io import StringIO 
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import copy
from collections import namedtuple
from math import dist

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

# The sizes of the ten regular components are 4 × 5, 4 × 6, 5 × 20, 6 × 9, 6 × 10, 6 × 11,
# 7 × 8, 7 × 12, 10 × 10, 10 × 20, respectively.
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

def other_components(component):
    others = copy.deepcopy(components)
    others.remove(component)
    return others

WIDTH = 30
HEIGHT = 30
Point = namedtuple("Point", "x y")
def tl(rect):
    return Point(rect[0], rect[1])

def tr(rect):
    return Point(rect[0] + rect[2], rect[1])

def bl(rect):
    return Point(rect[0], rect[1] + rect[3])

def br(rect):
    return Point(rect[0] + rect[2], rect[1] + rect[3])

all_components_in_bound = [
    And([
        tl(c).x >= 0,
        tl(c). y >= 0,
        br(c).x <= WIDTH,
        br(c).y <= HEIGHT]) 
for (c,(w,h)) in zip(components, COMPONENTS_TUPLES)]

no_components_overlap = [
    And([
        (Or([
            tr(c).x <= bl(o).x,
            bl(c).x >= tr(o).x,
            tr(c).y >= bl(o).y,
            bl(c).y <= tr(o).y,
        ]))
    for o in other_components(c)])
for c in components]

def eq(p1, p2):
    return And(p1.x == p2.x, p1.y == p2.y)

def touch(c1, c2):
    return And([Or([
        And([tl(c1).x == tr(c2).x, Or([
            And(tr(c1).y <= bl(c2).y, bl(c2).y <= br(c1).y),
            And(tr(c1).y <= tl(c2).y, tl(c2).y <= br(c1).y),
            ]),
        Not(tr(c1).y == bl(c2).y),
        Not(bl(c1).y == tl(c2).y)
            ]), # Left right
        And([tr(c1).x == tl(c2).x, Or([
            And(tr(c1).y <= bl(c2).y, bl(c2).y <= br(c1).y),
            And(tr(c1).y <= tl(c2).y, tl(c2).y <= br(c1).y),
            ]),
        Not(tr(c1).y == bl(c2).y),
        Not(bl(c1).y == tl(c2).y)
            ]), # Right left
        And([tl(c1).y == bl(c2).y, Or([
            And(bl(c1).x <= tr(c2).x, tr(c2).x <= br(c1).x),
            And(bl(c1).x <= tl(c2).x, tl(c2).x <= br(c1).x),
        ]),
        Not(bl(c1).x == tr(c2).x),
        Not(br(c1).x == tl(c2).x)
        ]), # Top bottom
        And([bl(c1).y == tl(c2).y, Or([
            And(bl(c1).x <= tr(c2).x, tr(c2).x <= br(c1).x),
            And(bl(c1).x <= tl(c2).x, tl(c2).x <= br(c1).x),
        ]),
        Not(bl(c1).x == tr(c2).x),
        Not(br(c1).x == tl(c2).x)
        ]), # Bottom top
    ])
    ])

D = 18

def get_center(rect):
    return Point(tl(rect).x + rect[2] / 2, tl(rect).y + rect[3] /2)

connected_to_power = [
    Or([
        touch(co, po) for po in power_components
    ]) for co in regular_components
]

#print(connected_to_power[0])

p1 = power_components[0]
p2 = power_components[1]

power_component_distance = [Or([
    get_center(p1).x >= get_center(p2).x + D,
    get_center(p2).x >= get_center(p1).x + D,
    get_center(p1).y >= get_center(p2).y + D,
    get_center(p2).y >= get_center(p1).y + D,
])]

print(power_component_distance)

s = Solver()
print("Solving")
s.add(flatten(components_sizes) + all_components_in_bound + no_components_overlap + connected_to_power + power_component_distance)
s.check()
m = s.model()

results = {var: m.evaluate(var) for var in flatten(power_components)}
print(results)

#define Matplotlib figure and axis
fig, ax = plt.subplots()
fig.set_size_inches(10, 10)

def plot_rects(comps: list, facecolor=None):
    ax.plot([0, 0],[0, WIDTH])
    ax.plot([0, WIDTH],[0, 0])
    colors = ["red", "green", "blue", "orange", "gray", "purple"]
    for n, rect in enumerate(comps):
        x = m.evaluate(rect[0]).as_long()
        y = m.evaluate(rect[1]).as_long()
        w = m.evaluate(rect[2]).as_long()
        h = m.evaluate(rect[3]).as_long()
        color = facecolor if facecolor is not None else colors[n % len(colors)]
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor="white"))


plot_rects(regular_components)
plot_rects(power_components, "black")
#create simple line plot


#add rectangle to plot


#display plot
plt.show()
