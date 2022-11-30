import traceback
from inspect import getsourcelines
import sys
from types import CodeType, FrameType
from typing import TextIO, Set, Optional, Any, Dict

from debuggingbook.Debugger import Debugger

from exercise_02.test import debug_main


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

    def __init__(self, *, file: TextIO = sys.stdout) -> None:
        """Create a new interactive debugger."""
        self.stepping: bool = True
        self.breakpoints: Set[int] = set()
        self.interact: bool = True
        self.next: bool = False

        self.frame: FrameType
        self.event: Optional[str] = None
        self.arg: Any = None

        self.local_vars: Dict[str, Any] = {}

        super().__init__(file=file)

    def stop_here(self) -> bool:
        """Return True if we should stop"""
        return self.stepping or self.frame.f_lineno in self.breakpoints or self.next


    def break_command(self, arg: str = "") -> None:
        """Set a breakoint in given line. If no line is given, list all breakpoints"""

        source_lines, line_number = getsourcelines(self.frame.f_code)
        start = line_number
        end = start + len(source_lines)-1
        if arg:
            try:
                l_no = int(arg)
                """for line in source_lines:
                    lines.append(line_no)
                    line_no += 1"""
                if int(arg) < start or int(arg) > end:
                    raise IndexError
                else:
                    self.breakpoints.add(int(arg))
                    self.log("Breakpoints:", self.breakpoints)
            except IndexError:
                self.log(f"line number {int(arg)} out of bound ({start} - {end})")
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

        self.local_vars = self.frame.f_locals
        sep = arg.find('=')
        if sep > 0:
            try:
                var = arg[:sep].strip()
                expr = arg[sep + 1:].strip()
                if not var.isidentifier():
                    raise SyntaxError
                elif var not in self.local_vars:
                    self.log(f"Warning: A new variable '{var}' is created")
                    self.local_vars[var] = expr
                else:
                    self.local_vars[var] = expr
            except SyntaxError:
                self.log(f"SyntaxError: '{var}' is not an identifier")
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

    def next_command(self, arg: str = "") -> None:
        """Execute up to the next line skipping functions if any"""

        if self.event=="call":
                self.continue_command()
        elif self.event==None:
            self.step_command()
        elif self.event=="return":
            self.next = True







    pass

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("No input file", file=sys.stderr)
        exit(1)

    module_name = sys.argv[1][:-3] # remove .py
    exec(f"from {module_name} import debug_main")

    with Debugger():
        debug_main()
