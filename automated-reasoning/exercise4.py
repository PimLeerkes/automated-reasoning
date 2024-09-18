from z3 import *

ITERATIONS = 10

a = [Int(f"a_{i}") for i in range(ITERATIONS+1)]
b = [Int(f"b_{i}") for i in range(ITERATIONS+1)]


#the preconditions:
preconditions = And(a[0] == 1, b[0] == 1)

#the for loop with the if statement
forloop = And([Or(And(a[i] == a[i-1] + 2*b[i-1], b[i] == b[i-1] + i), And(a[i] == a[i-1] + i, b[i] == b[i-1] + a[i])) for i in range(1,ITERATIONS+1)])

#forloop = Or(And([And(a[i] == a[i-1] + 2*b[i-1], b[i] == b[i-1] + i) for i in range(1,ITERATIONS+1)]), And([And(a[i] == a[i-1] + i, b[i] == b[i-1] + a[i]) for i in range(1,ITERATIONS+1)]))

#the post condition
postcondition = b[ITERATIONS-1] == 700 + 10

#it will not reach crash for n=1, 3, 5, 8, 10

phi = And(preconditions, forloop, postcondition)

solve(phi)

