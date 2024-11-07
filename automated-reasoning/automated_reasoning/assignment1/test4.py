
def UnsafeProgram(n):
    a = 1
    b = 1

    for i in range(1,11):
        if True:
            a = a + 2*b
            b = b + i
        else:
            a = a + i
            b = a + b

    if b == 700 + n:
        print("crash")

    return b

for i in range(1,11):
    b = UnsafeProgram(i)
    print(b)
