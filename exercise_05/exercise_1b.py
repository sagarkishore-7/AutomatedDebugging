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


def equal(x, y):
    if x == y:
        return 1
    else:
        return 0


def greater(x, y):
    if x > y:
        return 1
    else:
        return 0


def lesser(x, y):
    if x < y:
        return 1
    else:
        return 0


class PredicateCollector(Collector):

    def __init__(self) -> None:
        super().__init__()
        self.predicates: Dict[str, Predicate] = dict()

    def collect(self, frame: FrameType, event: str, arg: Any) -> None:
        if event != 'call':
            return
        a = inspect.getargvalues(frame)
        arg_list = a.locals
        #print(arg_list)
        func_name = frame.f_code.co_name

        """pred = Predicate(f'{func_name}({arg}')
        pred.true = 0
        pred.observed = 1"""

        for arg, value in arg_list.items():
            if isinstance(value, int) or isinstance(value, float):
                pred = Predicate(f'{func_name}({arg} == 0)', 0, 0, equal(value, 0), 0, 0, 1)
                self.predicates[pred.rpr] = pred

                pred = Predicate(f'{func_name}({arg} > 0)', 0, 0, greater(value, 0), 0, 0, 1)
                self.predicates[pred.rpr] = pred

                pred = Predicate(f'{func_name}({arg} < 0)', 0, 0, lesser(value, 0), 0, 0, 1)
                self.predicates[pred.rpr] = pred

                for next_arg, next_value in arg_list.items():
                    if arg != next_arg:
                        pred = Predicate(f'{func_name}({arg} == {next_arg})', 0, 0, equal(value, next_value), 0, 0, 1)
                        self.predicates[pred.rpr] = pred

                        pred = Predicate(f'{func_name}({arg} < {next_arg})', 0, 0, lesser(value, next_value), 0, 0, 1)
                        self.predicates[pred.rpr] = pred

                        pred = Predicate(f'{func_name}({arg} > {next_arg})', 0, 0, greater(value, next_value), 0, 0, 1)
                        self.predicates[pred.rpr] = pred

def test_collection():
    with PredicateCollector() as pc:
        ackermann(0, 1)
    results = {
        'ackermann(m == 0)': (1, 1),
        'ackermann(m < 0)': (0, 1),
        'ackermann(m > 0)': (0, 1),
        'ackermann(m < n)': (1, 1),
        'ackermann(m > n)': (0, 1),
        'ackermann(n == 0)': (0, 1),
        'ackermann(n < 0)': (0, 1),
        'ackermann(n > 0)': (1, 1),
        'ackermann(n < m)': (0, 1),
        'ackermann(n > m)': (1, 1),
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
