from debuggingbook.StatisticalDebugger import DifferenceDebugger
from typing import Optional, Set, Any

from predicate import Predicate
from exercise_1a import failure, context, increase
from exercise_1b import PredicateCollector, ackermann


class PredicateDebugger(DifferenceDebugger):
    
    def __init__(self, log: bool = False):
        super().__init__(collector_class=PredicateCollector, log=log)
    
    def all_predicates(self) -> Set[Any]:
        """Return a set of all predicates observed."""
        # TODO: implement
        return set()
    

def test_debugger():
    epsilon = 0.000001
    results = {
        'ackermann(m == 0)': (1/3, 1/3, 0),
        'ackermann(m < 0)':  (0,   1/3, -1/3),
        'ackermann(m > 0)':  (0,   1/3, -1/3),
        'ackermann(m < n)':  (0.5, 1/3, 0.5 - 1/3),
        'ackermann(m > n)':  (0,   1/3, -1/3),
        'ackermann(n == 0)': (0,   1/3, -1/3),
        'ackermann(n < 0)':  (0,   1/3, -1/3),
        'ackermann(n > 0)':  (0.5, 1/3, 0.5 - 1/3),
        'ackermann(n < m)':  (0,   1/3, -1/3),
        'ackermann(n > m)':  (0.5, 1/3, 0.5 - 1/3),
        'ackermann(m == n)': (0,   1/3, -1/3),
        'ackermann(n == m)': (0,   1/3, -1/3),
    }
    pd = PredicateDebugger()

    with pd.collect_pass():
        ackermann(3, 3)
    with pd.collect_pass():
        ackermann(0, 0)
    with pd.collect_fail():
        ackermann(0, 1)
    
    preds = pd.all_predicates()
    
    for p in results:
        assert Predicate(p) in preds, f'{p} not in all_predicates() result'
        
    for p in preds:
        f, c, i = results[p.rpr]
        assert abs(failure(p) - f) < epsilon, f'Failure for {p} was wrong, expected {f}, was {failure(p)}' 
        assert abs(context(p) - c) < epsilon, f'Context for {p} was wrong, expected {c}, was {context(p)}' 
        assert abs(increase(p) - i) < epsilon, f'Increase for {p} was wrong, expected {i}, was {increase(p)}' 
        

if __name__ == '__main__':
    test_debugger()
    print('Successful')
