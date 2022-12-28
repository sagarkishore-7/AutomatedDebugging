from predicate import Predicate

def failure(p: Predicate) -> float:
    zero_error = 0
    try:
        a = p.failing_true/(p.failing_true+p.successful_true)
    except(ZeroDivisionError):
        zero_error = 1

    if zero_error:
        return 0
    else:
        return a

def context(p: Predicate) -> float:
    zero_error = 0
    try:
        a = p.failing_observed/(p.failing_observed+p.successful_observed)
    except(ZeroDivisionError):
        zero_error = 1

    if zero_error:
        return 0
    else:
        return a

def increase(p: Predicate) -> float:
    return failure(p)-context(p)

def test_metrics():
    epsilon = 0.000001
    results = [
        (Predicate('f(x < y)', 1, 2, 3, 1, 3, 4), 1/3, 0.25, 1/3 - 0.25),
        (Predicate('f(y == z)', 2, 2, 4, 3, 3, 6), 0.5, 0.5, 0),
        (Predicate('f(z < x)', 4, 0, 4, 4, 4, 8), 1, 0.5, 0.5)
    ]
    for p, f, c, i in results:
        assert abs(failure(p) - f) < epsilon, f'Failure for {p} was wrong' 
        assert abs(context(p) - c) < epsilon, f'Context for {p} was wrong' 
        assert abs(increase(p) - i) < epsilon, f'Increase for {p} was wrong' 
        

if __name__ == '__main__':
    test_metrics()
    print('Successful')