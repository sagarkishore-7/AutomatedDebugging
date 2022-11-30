import traceback
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
    def break_command(self, arg: str = "") -> None:
        """Set a breakoint in given line. If no line is given, list all breakpoints"""

        lines = []
        source_lines, line_number = getsourcelines(self.frame.f_code)
        line_no = line_number
        if arg:
            try:
                l_no = int(arg)
                for line in source_lines:
                    lines.append(line_no)
                    line_no += 1
                if int(arg) in lines:
                    self.breakpoints.add(int(arg))
                    self.log("Breakpoints:", self.breakpoints)
                else:
                    raise IndexError
            except IndexError:
                self.log(f"line number {int(arg)} out of bound ({lines[0]} - {lines[-1]})")
            except ValueError:
                self.log(f"Expect a line number, but found '{arg}'")
        else:
            self.log("Breakpoints:", self.breakpoints)

    def delete_command(self, arg: str = "") -> None:
        """Delete breakoint in line given by `arg`.
           Without given line, clear all breakpoints"""

        if arg:
            try:
                l_no = int(arg)
                self.breakpoints.remove(int(arg))
            except ValueError:
                self.log(f"Expect a line number, but found {arg}")
            except KeyError:
                self.log(f"No such breakpoint: {arg}")
        else:
            self.breakpoints = set()
        self.log("Breakpoints:", self.breakpoints)

    def assign_command(self, arg: str) -> None:
        """Use as 'assign VAR=VALUE'. Assign VALUE to local variable VAR."""

        sep = arg.find('=')
        if sep > 0:
            try:
                var = arg[:sep].strip()
                expr = arg[sep + 1:].strip()
                if not var.isidentifier():
                    raise SyntaxError
                elif var not in self.local_vars:
                    self.log(f"Warning: A new variable {var} is created")
                else:
                    pass
            except SyntaxError:
                self.log(f"SyntaxError: {var} is not an identifier")
        else:
            self.help_command("assign")
            return

        vars = self.local_vars
        try:
            vars[var] = eval(expr, self.frame.f_globals, vars)
        except Exception as err:
            self.log(f"{err.__class__.__name__}: {err}")

    def where_command(self, arg):
        """Prints Traceback (most recent call last)"""

        caller = self.frame.f_back
        self.log("Traceback (most recent call last):")
        if self.frame.f_lineno != caller.f_lineno and self.frame.f_code.co_filename == caller.f_code.co_filename:
            z = CallInfo(caller.f_code, caller.f_lineno)
            self.log(z)
        s = CallInfo(self.frame.f_code, self.frame.f_lineno)
        self.log(s)

    def next_command(self):
        """Prints the next line ready for execution"""





    pass

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("No input file", file=sys.stderr)
        exit(1)

    module_name = sys.argv[1][:-3] # remove .py
    exec(f"from {module_name} import debug_main")

    with Debugger():
        debug_main()
