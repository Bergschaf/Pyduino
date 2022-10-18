import random

def mergesort(lst):
    if len(lst) <= 1:
        return lst
    mid = len(lst) // 2
    left = mergesort(lst[:mid])
    right = mergesort(lst[mid:])
    res = []
    while left and right:
        if left[0] < right[0]:
            res.append(left.pop(0))
        else:
            res.append(right.pop(0))
    res.extend(left)
    res.extend(right)

    return res

if __name__ == '__main__':
    print(boggoSort([random.randint(1,1000) for i in range(3)]))
