from inspect import getsourcelines
import sys
from types import CodeType
from debuggingbook.Debugger import Debugger

class CallInfo:
    def __init__(self, caller: CodeType, line_no: int) -> None:
        self.caller = caller
        self.loc = line_no

    def __repr__(self) -> str:
        head = f'File "{self.caller.co_filename}", line {self.loc}, in {self.caller.co_name}'
        lines, start = getsourcelines(self.caller)
        code = lines[self.loc - start].strip()
        return f'{head}\n  {code}'

class Debugger(Debugger):
    pass

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("No input file", file=sys.stderr)
        exit(1)

    module_name = sys.argv[1][:-3] # remove .py
    exec(f"from {module_name} import debug_main")

    with Debugger():
        debug_main()
