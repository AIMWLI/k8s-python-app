import random


def quicksort(arr):
    if len(arr) < 2:
        return arr
    pivot = arr[0]
    left = [x for x in arr[1:] if x <= pivot]
    right = [x for x in arr[1:] if x > pivot]
    return quicksort(left) + [pivot] + quicksort(right)


def mergesort(arr):
    if len(arr) < 2:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def heapsort(arr):
    def heapify(a, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        if l < n and a[l] > a[largest]:
            largest = l
        if r < n and a[r] > a[largest]:
            largest = r
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            heapify(a, n, largest)

    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)
    return arr


def insertion_sort(arr, left, right):
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


MIN_MERGE = 32


def timsort(arr):
    n = len(arr)
    if n < 2:
        return arr
    for start in range(0, n, MIN_MERGE):
        end = min(start + MIN_MERGE - 1, n - 1)
        insertion_sort(arr, start, end)
    size = MIN_MERGE
    while size < n:
        for left in range(0, n, size * 2):
            mid = left + size - 1
            right = min(left + size * 2 - 1, n - 1)
            if mid < right:
                merge(arr, left, mid, right)
        size *= 2
    return arr


def merge(arr, left, mid, right):
    left_part = arr[left:mid + 1]
    right_part = arr[mid + 1:right + 1]
    i = j = 0
    k = left
    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            j += 1
        k += 1
    while i < len(left_part):
        arr[k] = left_part[i]
        i += 1
        k += 1
    while j < len(right_part):
        arr[k] = right_part[j]
        j += 1
        k += 1


def dual_pivot_quicksort(arr):
    n = len(arr)
    if n < 2:
        return arr
    return _dual_pivot(arr, 0, n - 1)


def _dual_pivot(arr, low, high):
    if low < high:
        if arr[low] > arr[high]:
            arr[low], arr[high] = arr[high], arr[low]
        p, q = arr[low], arr[high]
        i = low + 1
        k = low + 1
        g = high - 1
        while k <= g:
            if arr[k] < p:
                arr[k], arr[i] = arr[i], arr[k]
                i += 1
            elif arr[k] > q:
                while arr[g] > q and k < g:
                    g -= 1
                arr[k], arr[g] = arr[g], arr[k]
                g -= 1
                if arr[k] < p:
                    arr[k], arr[i] = arr[i], arr[k]
                    i += 1
            k += 1
        i -= 1
        g += 1
        arr[low], arr[i] = arr[i], arr[low]
        arr[high], arr[g] = arr[g], arr[high]
        _dual_pivot(arr, low, i - 1)
        _dual_pivot(arr, i + 1, g - 1)
        _dual_pivot(arr, g + 1, high)
    return arr
