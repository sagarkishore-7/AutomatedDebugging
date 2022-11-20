from functools import wraps
level = 0

def trace(func):
    func_name = func.__name__
    seperator = " "

    @wraps(func)
    def traced_func(*args):
        if func_name == fib.__name__:
            n = args[0]
            print(f'{seperator * level}call with n = {n}')
        else:
            ar = args[0]
            l = args[1]
            r = args[2]
            print(f'{seperator * level}call with arr = {ar}, l = {l}, r = {r}')
        increase_level()
        increase_level()
        result = func(*args)
        decrease_level()
        decrease_level()
        print(f'{seperator * level}return {result}')

        return result
    return traced_func
def increase_level():
    global level
    level += 1

    
def decrease_level():
    global level
    level -= 1
    
    
def log(s: str = ''):
    print(s)

    
# TODO: change this function
def fib(n: int) -> int:
    if n == 0:
        return 0
    if n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


# https://www.geeksforgeeks.org/python-program-for-merge-sort/
def merge(arr, l, m, r): # auxiliary function, do not trace
    n1 = m - l + 1
    n2 = r - m

    L = [0] * (n1)
    R = [0] * (n2)

    for i in range(0, n1):
        L[i] = arr[l + i]

    for j in range(0, n2):
        R[j] = arr[m + 1 + j]

    i = 0
    j = 0
    k = l

    while i < n1 and j < n2:
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1

    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1

    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1


# TODO: change this function
def merge_sort(arr, l, r): # main function
    if l < r:
        m = l + (r - l) // 2

        merge_sort(arr, l, m)       # <--- trace this
        merge_sort(arr, m + 1, r)   # <--- trace this
        merge(arr, l, m, r)         # <--- do not trace this!

    return arr


if __name__ == '__main__':
    fib = trace(fib)
    fib(4)
    log()
    arr = [12, 11, 13, 5, 6, 7]
    merge_sort = trace(merge_sort)
    merge_sort(arr, 0, len(arr) - 1)