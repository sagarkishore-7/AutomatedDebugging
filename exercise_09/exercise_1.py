from typing import List, Tuple

### Buggy programs ###

def search_buggy_1(x: int, seq: List[int]) -> int:
    for i in range(len(seq)):
        if x <= seq[i]:
            return i
        else:
            return len(seq)

def search_buggy_2(x: int, seq: List[int]) -> int:
    if x < seq[0]:
        return 0
    elif x > seq[-1]:
        return len(seq)
    for i, elem in enumerate(seq):
        if x <= elem:
            return i

### Reference program ###
def search_correct(x: int, seq: List[int]) -> int:
    for i in range(len(seq)):
        if x <= seq[i]:
            return i
    return len(seq)

### Test suite ###
TESTCASES: List[Tuple[Tuple[int, List[int]], int]] = [
    ((4, [1, 2, 3]), 3),
    ((4, [1, 2, 3, 4]), 3),
    ((4, [4, 3, 2, 1]), 0),
    ((4, [3, 4, 2, 1]), 1),
    ((4, [3, 2, 4, 1]), 2),
    ((4, [4, 4, 4, 4]), 0),
    ((5, [4, 3, 2, 1]), 4),
    ((5, [4, 3, 2, 5]), 3),
    ((2, [3, 2, 4, 1]), 0)
]

### Repair ###

def search_buggy_1_test(x, seq, expected):
    assert search_buggy_1(x, seq) == expected

def search_buggy_2_test(x, seq, expected):
    assert search_buggy_2(x, seq) == expected

if __name__ == '__main__':
    assert 0 < len(TESTCASES) <= 10, 'testcases length not in range (0, 10]'
    for (x, seq), expected in TESTCASES:
        assert search_correct(x, seq) == expected, f'testcase (({x}, {seq}), {expected}) is wrong'

    from debuggingbook.StatisticalDebugger import OchiaiDebugger
    from debuggingbook.Repairer import Repairer

    for i in range(3):
        print('--> repairing search_buggy_1')
        debugger1 = OchiaiDebugger()
        for (x, seq), expected in TESTCASES:
            with debugger1:
                search_buggy_1_test(x, seq, expected)
        repairer = Repairer(debugger1)
        tree, fitness = repairer.repair()
        if fitness == 1.0:
            print('--> Found candidate with fitness=1.0 for search_buggy_1')
            break
    
    for i in range(3):
        print('--> repairing search_buggy_2')
        debugger2 = OchiaiDebugger()
        for (x, seq), expected in TESTCASES:
            with debugger2:
                search_buggy_2_test(x, seq, expected)
        repairer = Repairer(debugger2)
        tree, fitness = repairer.repair()
        if fitness == 1.0:
            print('--> Found candidate with fitness=1.0 for search_buggy_2')
            break
