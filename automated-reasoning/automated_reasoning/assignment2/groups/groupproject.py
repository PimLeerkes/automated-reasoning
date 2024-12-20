from z3 import *

import sys 
import string
import math
import copy

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
  return {student_names[n]: project_names[assignment[n]] for n in range(N)}

def get_goodness(assignment: list[int]) -> list[int]:
  # for n in range(N):
  #   for p in range(P):
  #     r = get_rank_by_id(n, p)
  #     print(f"{n} {p} {r}")
  return [sum([int(get_rank_by_id(n, p) -1 == r and assignment[n] == p)
               for n in range(N) for p in range(P)]) 
  for r in range(0, P)]

def find_assignment(lower_bound_attempt: list):
  V_ASSIGNMENT = [Int(f"A_{n}") for n in range(N)]
  F_ASSIGNMENT_BOUND = [And(a_n >= 0, a_n < P) for a_n in V_ASSIGNMENT]
  F_GROUP_SIZES = [Or(Sum([a_n == p for a_n in V_ASSIGNMENT]) == math.floor(N/P),
                      Sum([a_n == p for a_n in V_ASSIGNMENT]) == math.ceil(N/P))
                   for p in range(P)]
  V_GOODNESS = [Int(f"N_A_{R}") for R in range(P)]
  F_GOODNESS_1 = [V_GOODNESS[r] == Sum([
    And(get_rank_by_id(n, p) -1 == r, V_ASSIGNMENT[n] == p)
    for n in range(N) for p in range(P)]) for r in range(P)]
  
  F_LOWER_BOUND_ATTEMPT = [V_GOODNESS[r] <= v for r,v in enumerate(lower_bound_attempt)]
  # print(lower_bound_attempt)
  # print(F_LOWER_BOUND_ATTEMPT)
  # if try_rank:
  #   F_FIND_BETTER = [V_]
  #   [V_GOODNESS[r] == 0 for r in range(zero_index, P)]
  # else:
  #   F_FIND_BETTER = [Or([
  #   And(V_GOODNESS[R] < goodness_b[R],
  #       And([V_GOODNESS[r] == goodness_b[r] for r in range(R+1, P)])
  #       )
  #   for R in range(P)
  # ])]
  
  
  phi = F_ASSIGNMENT_BOUND + F_GROUP_SIZES + F_GOODNESS_1 + F_LOWER_BOUND_ATTEMPT
  
  V_ALL_VARS = V_ASSIGNMENT
  
  s = Solver()
  s.add(phi)
  s.check()
  try:
    m = s.model()
    res = [int(str(m.evaluate(var))) for var in V_ASSIGNMENT]
    return res
  except:
    return None

def optimize_solution2(goodness_b, rank):
  if rank == 0:
    return find_assignment(goodness_b)
  decreasing = goodness_b[rank] - 1
  constraint_a = [N for _ in range(rank)] + [decreasing] + [goodness_b[i] for i in range(rank+1, P)]
  print(f"\nrank: {rank}")
  print("previous", goodness_b)
  print("trying", constraint_a)
  a = find_assignment(constraint_a)
  if a is None:
    return optimize_solution(goodness_b, rank-1)
  else:
    return optimize_solution2(get_goodness(a), rank)

def optimize_solution(goodness_b, rank):
  if rank == 0:
    return find_assignment(goodness_b)
  constraint_a = [N for _ in range(rank)] + [0] + [goodness_b[i] for i in range(rank+1, P)]
  print(f"\nrank: {rank}")
  print("previous", goodness_b)
  print("trying", constraint_a)
  a = find_assignment(constraint_a)
  if a is None:
    return optimize_solution2(goodness_b, rank)
  else:
    return optimize_solution(get_goodness(a), rank-1)

solution = optimize_solution([N for _ in range(P)], P-1)
#solution = optimize_solution([N for _ in range(P)], P-1, True)
#solution = optimize_solution_delta([N for _ in range(P)], P-1, N)
if solution is not None:
  print_solution(to_names(solution))
print("****************************************************************************")

