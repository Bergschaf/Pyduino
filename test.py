import random


def selectionsort(arr):
    res = []
    for i in range(len(arr)):
        minimum = min(arr)
        res.append(minimum)
        arr.remove(minimum)
    return res


def mergesort(arr):
    if len(arr) < 2:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    res = []
    while left and right:
        if left[0] > right[0]:
            res.append(left[0])
            left.remove(left[0])
        else:
            res.append(right[0])
            right.remove(right[0])
    res += left
    res += right
    return res


def heapsort(arr):
    res = []
    while arr:
        res.append(max(arr))
        arr.remove(max(arr))
    return res


if __name__ == '__main__':
    x = 2
    print(type(x))
    if input() == "1":
        x = True
    else:
        x = 3

    print(x + "ahhlo")








