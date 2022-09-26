it = enumerate([1,2,3,4,5,6,7,8,9])
for i in it:
    print(i)
    if i[0] == 5:
        print(next(it), "next")