import inspect
import sys
from typing import Callable, TextIO
from debuggingbook.Tracer import Tracer

from exercise_2 import *


def param_names(func: Callable):
    return inspect.getfullargspec(func).args


class RecursiveTracer(Tracer):

    def __init__(self, func: Callable, file: TextIO = sys.stdout) -> None:
        self.func: Callable = func
        super().__init__(file=file)

        pass

    def traceit(self, frame, event, arg, indent=[0]):
        # print(event, "Line no.", frame.f_lineno, frame.f_code.co_name, frame.f_locals)
        if event == "call":
            if 'n' in frame.f_locals:
                value_of_n = frame.f_locals['n']
                print(" " * indent[0] + 'call with', param_names(fib), "=", repr(value_of_n))
            indent[0] += 2
        elif event == "return":
            if indent[0] == 2:
                indent[0] = 0
                print(" " * (indent[0] - 1) + "return", arg)
            else:
                indent[0] -= 2
                print(" " * (indent[0] - 1), "return", arg)
        return self


# with RecursiveTracer(func=fib):
#         fib(4)
# def fib_traced(self,n: int) -> int:
#     sys.settrace(self.traceit)
#     ret = fib(n)
#     sys.settrace(None)
#     return ret

######## Tests ########

if __name__ == '__main__':
    with RecursiveTracer(func=fib):
        fib(4)

    # the following is the expected log output:
    expected = """
call with n = 4
  call with n = 3
    call with n = 2
      call with n = 1
      return 1
      call with n = 0
      return 0
    return 1
    call with n = 1
    return 1
  return 2
  call with n = 2
    call with n = 1
    return 1
    call with n = 0
    return 0
  return 1
return 3
"""

    with RecursiveTracer(func=merge_sort):
        arr = [12, 11, 13, 5, 6, 7]
        merge_sort(arr, 0, len(arr) - 1)

    # the following is the expected log output:
    expected = """
call with arr = [12, 11, 13, 5, 6, 7], l = 0, r = 5
  call with arr = [12, 11, 13, 5, 6, 7], l = 0, r = 2
    call with arr = [12, 11, 13, 5, 6, 7], l = 0, r = 1
      call with arr = [12, 11, 13, 5, 6, 7], l = 0, r = 0
      return [12, 11, 13, 5, 6, 7]
      call with arr = [12, 11, 13, 5, 6, 7], l = 1, r = 1
      return [12, 11, 13, 5, 6, 7]
    return [11, 12, 13, 5, 6, 7]
    call with arr = [11, 12, 13, 5, 6, 7], l = 2, r = 2
    return [11, 12, 13, 5, 6, 7]
  return [11, 12, 13, 5, 6, 7]
  call with arr = [11, 12, 13, 5, 6, 7], l = 3, r = 5
    call with arr = [11, 12, 13, 5, 6, 7], l = 3, r = 4
      call with arr = [11, 12, 13, 5, 6, 7], l = 3, r = 3
      return [11, 12, 13, 5, 6, 7]
      call with arr = [11, 12, 13, 5, 6, 7], l = 4, r = 4
      return [11, 12, 13, 5, 6, 7]
    return [11, 12, 13, 5, 6, 7]
    call with arr = [11, 12, 13, 5, 6, 7], l = 5, r = 5
    return [11, 12, 13, 5, 6, 7]
  return [11, 12, 13, 5, 6, 7]
return [5, 6, 7, 11, 12, 13]
"""