from z3 import *

import sys 
import string
import random

########## read input ##########

inputfile = "example.txt"
if len(sys.argv) == 2:
    inputfile = sys.argv[1]

preferences = { }
with open(inputfile, 'r', encoding="utf-8") as file:
  for line in file:
    parts = line.strip().split(" ")
    if (len(parts) > 1):
      preference = {}
      name = parts[0]
      for p in parts[1:]:
        pair = p.split(":")
        preference[pair[0]] = int(pair[1])
      preferences[name] = preference

student_names = list(preferences.keys())
project_names = list(preferences[student_names[0]].keys())
N = len(student_names)
P = len(project_names)
student_names.sort()
project_names.sort()
minimum_group_size = int(N / P)
maximum_group_size = int((N + P - 1) / P)

# Given a student name (element of student_names) and the name of a project (element of
# project_names), this returns the preference-rank of the given project for the given student
def get_rank(student: string, proj: string):
  """Returns how this student ranks the project with this id"""
  return preferences[student][proj]

# Given the index of a student (0..N-1) and of a project (0..P-1), this returns the preference-rank
# of the given project for the given student
def get_rank_by_id(student_id: int, proj_id: int):
  """Returns how the student with this id ranks the book with this id"""
  return preferences[student_names[student_id]][project_names[proj_id]]

# Given a dictionary that assigns to every student name the name of that student's project, this
# prints the solution along with its goodness.  Use this to print the output!
def print_solution(solution):
  goodness = [ 0 for i in range(P) ]
  team = { proj : [] for proj in project_names }
  for student in student_names:
    rank = get_rank(student, solution[student])
    goodness[rank-1] = goodness[rank-1] + 1
    team[solution[student]].append(student)
  for proj in project_names:
    print("Project", proj, "has", len(team[proj]), "students:", end='')
    team[proj].sort();
    for student in team[proj]:
      print(" " + str(student), "(" + str(get_rank(student, proj)) + ")", end="")
    print()
  print("Overall goodness:", goodness)

########## your code goes here! ##########

def to_names(assignment: list[int]) -> list[str]:
  pass

def get_goodness(assignment: list[int]) -> list[int]:
  return [sum([int(get_rank_by_id(n, p) == r and assignment[n] == p)
               for n in range(N) for p in range(P)]) 
  for r in range(P)]

def find_better_assignment(goodness_b):
  V_ASSIGNMENT = [Int(f"A_{n}") for n in range(N)]
  F_ASSIGNMENT_BOUND = [And(a_n >= 0, a_n < P) for a_n in V_ASSIGNMENT]
  F_GROUP_SIZES = [Or(Sum([a_n == p for a_n in V_ASSIGNMENT]) == math.floor(N/P),
                      Sum([a_n == p for a_n in V_ASSIGNMENT]) == math.ceil(N/P))
                   for p in range(P)]
  # F_BETTER = Or([
  #   V_ASSIGNMENT[R] < goodness_b[R]
  # for R in range(P)])
  # print(F_BETTER)
  
  phi = F_ASSIGNMENT_BOUND + F_GROUP_SIZES
  
  V_ALL_VARS = V_ASSIGNMENT
  
  s = Solver()
  s.add(phi)
  s.check()
  try:
    m = s.model()
    res = [int(str(m.evaluate(var))) for var in V_ALL_VARS]
    return res
  except:
    return None

def best_solution() -> list[int]:
  w = [0 for n in range(N)] + [N]
  b = find_better_assignment(w)
  if b is None:
    print("Failure")
    return None
  while True:
    a = find_better_assignment(get_goodness(b))
    if a is None:
      return b
    b = a
    print("Found better assignment")
    print(b)
    print("Next iteration\n")

solution = best_solution()
if solution is not None:
  print_solution(to_names(solution))
print("****************************************************************************")

