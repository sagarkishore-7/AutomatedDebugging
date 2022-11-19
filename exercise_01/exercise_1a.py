from exercise_1 import convert_to_rgb
from types import FrameType, TracebackType
import sys

hex_str_assertion_error = 'azazaz'
hex_str_functional_error = 'ABABAB'

def traceit(frame: FrameType, event: str, arg):
   # print(frame.f_code.co_name, frame.f_locals)
    return traceit

def convert_to_rgb_traced(hex_str_assertion_error):
    sys.settrace(traceit)
    ret = convert_to_rgb(hex_str_assertion_error)
    sys.settrace(None)
    return ret


if __name__ == '__main__':
    try:
        convert_to_rgb_traced(hex_str_assertion_error)
    except AssertionError:
        print(f'{hex_str_assertion_error} triggered an AssertionError. Is this intended?')
    else:
        print(f'{hex_str_assertion_error} did not trigger an AssertionError. Is this intended?')
        
    print(f'{hex_str_functional_error} has the following rgb values: {convert_to_rgb(hex_str_functional_error)}. Is this correct?')

