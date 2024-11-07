from z3 import *

import sys 
import string
import random

########## read input ##########

inputfile = "ranking.txt"
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

print("********** delete this output; this is just to show the variables **********")
# N is the number of students
print("Number of students:", N)
# P is the number of projects
print("Number of projects:", P)
# minimum group size is the minimum number of students that should be assigned to each project
print("Minimum number of students per project group:", minimum_group_size)
# maximum group size is the minimum number of students that should be assigned to each project
print("Maximum number of students per project group:", maximum_group_size)
# student_names is the list of students
print("Students are called:", student_names)
# project_names is the list of projects
print("Projects are called:", project_names)
# for student in student_names and proj in project_names, get_rank(student, proj) indicates the
# ranking the given student assigns to the given project
print("Rank for student", student_names[0], "with project", project_names[P-1], "is:",
  get_rank(student_names[0], project_names[P-1]))
# for student in 0..N-1 and proj in 0..P-1, get_rank_by_id(student, proj) indicates the ranking the
# given student assigns to the corresponding project
print("Rank for student 0 with project id", P-1, "is:", get_rank_by_id(0, P-1))

# let's show a random output assignment
print("Here's a random solution (which might not comply with the group size requirements):")
randomsolution = {}
for student in student_names:
  randomsolution[student] = random.choice(project_names)
print_solution(randomsolution)
print("****************************************************************************")

