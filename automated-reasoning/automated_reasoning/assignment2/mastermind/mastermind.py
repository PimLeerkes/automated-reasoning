from z3 import *

import sys
import csv

########## read input ##########

if len(sys.argv) != 2:
    sys.exit("Expected exactly one runtime argument.")

lines = []
with open(sys.argv[1], newline="") as inputfile:
    reader = csv.reader(inputfile, delimiter=" ")
    for row in reader:
        if row != []: lines.append(row)

# line 1: N (length of the combination) and K (number of colours)
N = int(lines[0][0])
K = int(lines[0][1])

# remaining lines: guesses!
guesses = []
for line in lines[1:]:
  fullycorrect = int(line[0])
  wrongplace = int(line[1])
  guess = [int(line[i+3]) for i in range(N)]
  guesses.append( (guess, fullycorrect, wrongplace) )

######### some functions you may find useful ##########

def number_correct(guess):
  """Returns the number of correct colours at the correct position for the given guess"""
  return guess[1]

def number_partial(guess):
  """Returns the number of correct colours at the wrong position for the given guess"""
  return guess[2]

def get_list(guess):
  """return the list describing the full guess"""
  return guess[0]

# uncomment the following if you want to see the values of the main variables, and the output of the functions
#print(N)
#print(K)
#print(guesses)
#print(get_list(guesses[0]))
#print(number_correct(guesses[0]))
#print(number_partial(guesses[0]))

########## finding a possible combination ##########

# THIS IS WHERE YOUR CODE GOES

#we make the solution variables
S = [Int(f"s_{i}") for i in range(N)]

#we put a constraint on the value of S
S_constraint = And([And(0<s,s<=K) for s in S])

#for a we don't want duplicates in the solution
no_duplicates = And([And([Implies(i != j, S[i] != S[j]) for i in range(N)]) for j in range(len(S))])

#correct colors (same for a and b):
def correct(guess: list[int], n: int):
  return Sum([If(S[i] == get_list(guess)[i], 1, 0) for i in range(N)]) == n

#partially correct colors a:
def wrong_place_correct_color_a(guess, i):
  return And(S[i] != get_list(guess)[i], Or([S[j] == get_list(guess)[i] for j in range(N)]))

def partially_correct_a(guess, n):
  return Sum([If(wrong_place_correct_color_a(guess, i), 1, 0) for i in range(N)]) == n

#partially correct colors b:
def wrong_place_correct_color_b(guess, i):
  n_solution = Sum([If(And(S[k] == get_list(guess)[i], S[k] != get_list(guess)[k]),1,0) for k in range(N)])
  n_guess_lower_i = Sum([If(And(get_list(guess)[i] == get_list(guess)[j],S[j] != get_list(guess)[j]),1,0) for j in range(i)])

  return And(S[i] != get_list(guess)[i], n_solution > n_guess_lower_i, Or([And(S[j] == get_list(guess)[i], get_list(guess)[i] != get_list(guess)[j]) for j in range(N)]))

def partially_correct_b(guess, n):
  return Sum([If(wrong_place_correct_color_b(guess, i), 1, 0) for i in range(N)]) == n

#we combine all guesses together
all_guesses_a = And([And(correct(guess, number_correct(guess)), partially_correct_a(guess,number_partial(guess))) for guess in guesses])
all_guesses_b = And([And(correct(guess, number_correct(guess)), partially_correct_b(guess,number_partial(guess))) for guess in guesses])

#the resulting formulas for a and b
a = [all_guesses_a, no_duplicates, S_constraint]
b = [all_guesses_b, S_constraint]

solver = Solver()
solver.add(b)
if solver.check() == sat:
    model = solver.model()
    solution = [model[s].as_long() for s in S]


########## print the solution ##########

print("Solution:", end= '')
for s in solution:
  print(" " + str(s), end = '')
print()

