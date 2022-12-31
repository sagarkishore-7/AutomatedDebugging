from debuggingbook.StatisticalDebugger import Collector
from types import FrameType
from typing import Any, Dict
import inspect

from predicate import Predicate

def ackermann(m, n):
    if m == 0:
        return n + 1
    elif n == 0:
        return ackermann(m - 1, 1)
    else:
        return ackermann(m - 1, ackermann(m, n - 1))


class PredicateCollector(Collector):
    
    def __init__(self) -> None:
        super().__init__()
        self.predicates: Dict[str, Predicate] = dict()
    
    def collect(self, frame: FrameType, event: str, arg: Any) -> None:
        a = inspect.getargvalues(frame)
        func_name = frame.f_code.co_name

        for arg in a.args:
            """pred = Predicate(f"{func_name}({arg} == 0)")
            pred.true = 0
            pred.observed = 1"""
            if isinstance(a.locals[arg],float) or isinstance(a.locals[arg], int):
                pass
            else:
                break
            if a.locals[arg] == 0:
                self.predicates.update(
                    {f"{func_name}({arg} == 0)": Predicate(rpr=f"{func_name}({arg} == 0)", true=1, observed=1)})
            else:
                self.predicates.update(
                    {f"{func_name}({arg} == 0)": Predicate(rpr=f"{func_name}({arg} == 0)", true=0, observed=1)})
            if a.locals[arg] < 0:
                self.predicates.update(
                    {f"{func_name}({arg} < 0)": Predicate(rpr=f"{func_name}({arg} < 0)", true=1, observed=1)})
            else:
                self.predicates.update(
                    {f"{func_name}({arg} < 0)": Predicate(rpr=f"{func_name}({arg} < 0)", true=0, observed=1)})
            if a.locals[arg] > 0:
                self.predicates.update(
                    {f"{func_name}({arg} > 0)": Predicate(rpr=f"{func_name}({arg} > 0)", true=1, observed=1)})
            else:
                self.predicates.update(
                    {f"{func_name}({arg} > 0)": Predicate(rpr=f"{func_name}({arg} > 0)", true=0, observed=1)})
            for next_arg in a.args:
                if next_arg == arg:
                    continue
                if a.locals[arg] == a.locals[next_arg]:
                    self.predicates.update({f"{func_name}({arg} == {next_arg})": Predicate(
                        rpr=f"{func_name}({arg} == {next_arg})", true=1, observed=1)})
                    self.predicates.update({f"{func_name}({next_arg} == {arg})": Predicate(
                        rpr=f"{func_name}({next_arg} == {arg})", true=1, observed=1)})
                else:
                    self.predicates.update({f"{func_name}({arg} == {next_arg})": Predicate(
                        rpr=f"{func_name}({arg} == {next_arg})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({next_arg} == {arg})": Predicate(
                        rpr=f"{func_name}({next_arg} == {arg})", true=0, observed=1)})
                if a.locals[arg] < a.locals[next_arg]:
                    self.predicates.update({f"{func_name}({arg} < {next_arg})": Predicate(
                        rpr=f"{func_name}({arg} < {next_arg})", true=1, observed=1)})
                    self.predicates.update({f"{func_name}({next_arg} < {arg})": Predicate(
                        rpr=f"{func_name}({next_arg} < {arg})", true=0, observed=1)})
                else:
                    self.predicates.update({f"{func_name}({arg} < {next_arg})": Predicate(
                        rpr=f"{func_name}({arg} < {next_arg})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({next_arg} < {arg})": Predicate(
                        rpr=f"{func_name}({next_arg} < {arg})", true=1, observed=1)})
                if a.locals[arg] > a.locals[next_arg]:
                    self.predicates.update({f"{func_name}({arg} > {next_arg})": Predicate(
                        rpr=f"{func_name}({arg} > {next_arg})", true=1, observed=1)})
                    self.predicates.update({f"{func_name}({next_arg} > {arg})": Predicate(
                        rpr=f"{func_name}({next_arg} > {arg})", true=0, observed=1)})
                else:
                    self.predicates.update({f"{func_name}({arg} > {next_arg})": Predicate(
                        rpr=f"{func_name}({arg} > {next_arg})", true=0, observed=1)})
                    self.predicates.update({f"{func_name}({next_arg} > {arg})": Predicate(
                        rpr=f"{func_name}({next_arg} > {arg})", true=1, observed=1)})
        """self.predicates.update({f"{func_name}({arg} == 0)": Predicate(rpr=f"{func_name}({arg} == 0)", true=1, observed=1)})

        self.predicates.update({f"{func_name}({arg} == {next_arg})": Predicate(rpr=f"{func_name}({arg} == 0)", true=1, observed=1)})"""






        
def test_collection():
    with PredicateCollector() as pc:
        ackermann(0, 1)
    results = {
        'ackermann(m == 0)': (1, 1),
        'ackermann(m < 0)': (0, 1),
        'ackermann(m > 0)': (0, 1),
        'ackermann(m < n)':  (1, 1),
        'ackermann(m > n)':  (0, 1),
        'ackermann(n == 0)': (0, 1),
        'ackermann(n < 0)': (0, 1),
        'ackermann(n > 0)': (1, 1),
        'ackermann(n < m)':  (0, 1),
        'ackermann(n > m)':  (1, 1),
        'ackermann(m == n)': (0, 1),
        'ackermann(n == m)': (0, 1),
    }
    for pred in results:
        pred = pc.predicates[pred]
        p, o = results[pred.rpr]
        assert pred.true == p, f'True for {pred} was wrong, expected {p}, was {pred.true}' 
        assert pred.observed == o, f'Observed for {pred} was wrong, expected {o}, was {pred.observed}' 
        assert pred.failing_observed == pred.successful_observed == pred.failing_true == pred.successful_true == 0

        
if __name__ == '__main__':
    test_collection()
    print('Successful')
