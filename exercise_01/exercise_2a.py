import inspect
import sys
from typing import Callable, TextIO
from debuggingbook.Tracer import Tracer
from types import FrameType, TracebackType

from exercise_2 import *


def param_names(func: Callable):
    return inspect.getfullargspec(func).args


class RecursiveTracer(Tracer):
    def __init__(self, func: Callable, file: TextIO = sys.stdout) -> None:
        self.func: Callable = func
        super().__init__(file=file)
    def traceit(self, event, frame, arg):
        #func_name = func.__name__
        seperator =''
        depth = 0
        if event == "call":
            depth += 2
            if fib.__name__:
                if 'n' in frame.f_locals:
                    value_of_n = frame.f_locals['n']
                    print( seperator * depth + 'call with', param_names(fib), "=", repr(value_of_n))
            elif merge_sort.__name__:
                print( seperator * depth + 'call with', param_names(merge_sort), "=", repr(frame.f_locals))
        elif event == "return":
            print( seperator * depth + "return" + arg)
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