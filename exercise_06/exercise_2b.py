from debuggingbook.DynamicInvariants import InvariantAnnotator, INVARIANT_PROPERTIES

def mystery(x, y):
    if len(y) > 0:
        return x * y
    else:
        raise ValueError('len(y) <= 0')
        

def test_mystery():
    mystery(1, 'test')
    mystery(-1, 'test')
    

def run() -> InvariantAnnotator:
    # TODO
    pass


if __name__ == '__main__':
    print(run().function_with_invariants('mystery'))
