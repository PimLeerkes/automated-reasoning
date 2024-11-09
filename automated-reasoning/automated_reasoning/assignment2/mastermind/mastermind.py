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

from functools import reduce
def powerset(lst):
  """returns the 'powerlist' of a list"""
  return reduce(lambda result, x: result + [subset + [x] for subset in result],
                  lst, [[]])



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
no_duplicates = And([And([Implies(i != j, S[i] != S[j]) for i in range(len(S))]) for j in range(len(S))])


#correct colors:
def correct(guess: list[int], n: int):
  return Sum([If(S[i] == get_list(guess)[i],1,0) for i in range(N)]) == n
  #return Or([And(len(I) == n, And([S[i] == get_list(guess)[i] for i in I]))
  #              for I in powerset([n for n in range(N)])])


#partially correct colors:
def partially_correct(guess: list[int], n: int):
  return Sum([If(Or([And(k != i, S[k] == get_list(guess)[i]) for k in range(N)]), 1, 0) for i in range(N)]) == n
  #return Or([And(len(I) == n, And([Or([And(k != i, S[k] == get_list(guess)[i]) for k in range(N)]) for i in I]))
  #              for I in powerset([n for n in range(N)])])

#all_guesses_correct = And([correct(guess, number_correct(guess)) for guess in guesses])
#solve(And(no_duplicates,S_constraint,all_guesses_correct))

#we combine all guesses together
all_guesses = And([And(correct(guess, number_correct(guess)), partially_correct(guess,number_partial(guess))) for guess in guesses])


#the resulting formulas for a and b
a = [all_guesses, no_duplicates, S_constraint]
b = [all_guesses, S_constraint]

solver = Solver()
solver.add(a)
if solver.check() == sat:
    model = solver.model()
    solution = [model[s].as_long() for s in S]

########## print the solution ##########

print("Solution:", end= '')
for s in solution:
  print(" " + str(s), end = '')
print()

