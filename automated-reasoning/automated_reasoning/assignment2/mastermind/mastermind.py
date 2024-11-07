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

# remove this, since it's just to give an example for the output
solution = range(1,N+1)

########## print the solution ##########

print("Solution:", end= '')
for s in solution:
  print(" " + str(s), end = '')
print()

