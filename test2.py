n = 3
arr = [-4, 3, 2]
i = 1
z = 0
while i <= n:
    x = arr[i-1]
    if x < 0:
        y = x + 1
    else:
        y = x + 2
    z = y
    i = i + 1
print(z)