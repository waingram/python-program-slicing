def fact(n = 5):
    if n == 1:
        return n
    else:
        return n * fact(n-1)
    