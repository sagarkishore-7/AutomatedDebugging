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

        complete_set = {}

        for pass_list in self.pass_collectors():
            #print(pass_list)
            for pred_name, value in pass_list.predicates.items():
                if pred_name not in complete_set:
                    new_pred = Predicate(pred_name, 0, 0, 0, 0, 1, 1)
                    if value.true == 1:
                        new_pred = Predicate(pred_name, 0, 1, 1, 0, 1, 1)
                    complete_set[pred_name] = new_pred
                    #print(complete_set)
                else:
                    temp_pred = complete_set[pred_name]
                    temp_pred.observed += 1
                    temp_pred.successful_observed += 1
                    if value.true == 1:
                        temp_pred.successful_true += 1
                        temp_pred.true += 1
                    complete_set[pred_name] = temp_pred
                    #print(temp_pred)
                    #print(complete_set)

        for fail_list in self.fail_collectors():
            for pred_name, value in fail_list.predicates.items():
                if pred_name not in complete_set:
                    new_pred = Predicate(pred_name, 0, 0, 0, 1, 0, 1)
                    if value.true == 1:
                        new_pred = Predicate(pred_name, 1, 0, 1, 1, 0, 1)
                    complete_set[pred_name] = new_pred
                else:
                    temp_pred = complete_set[pred_name]
                    temp_pred.observed += 1
                    temp_pred.failing_observed += 1
                    if value.true == 1:
                        temp_pred.failing_true += 1
                        temp_pred.true += 1
                    complete_set[pred_name] = temp_pred
        #print(complete_set)
        return set(complete_set.values())


def test_debugger():
    epsilon = 0.000001
    results = {
        'ackermann(m == 0)': (1 / 3, 1 / 3, 0),
        'ackermann(m < 0)': (0, 1 / 3, -1 / 3),
        'ackermann(m > 0)': (0, 1 / 3, -1 / 3),
        'ackermann(m < n)': (0.5, 1 / 3, 0.5 - 1 / 3),
        'ackermann(m > n)': (0, 1 / 3, -1 / 3),
        'ackermann(n == 0)': (0, 1 / 3, -1 / 3),
        'ackermann(n < 0)': (0, 1 / 3, -1 / 3),
        'ackermann(n > 0)': (0.5, 1 / 3, 0.5 - 1 / 3),
        'ackermann(n < m)': (0, 1 / 3, -1 / 3),
        'ackermann(n > m)': (0.5, 1 / 3, 0.5 - 1 / 3),
        'ackermann(m == n)': (0, 1 / 3, -1 / 3),
        'ackermann(n == m)': (0, 1 / 3, -1 / 3),
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
