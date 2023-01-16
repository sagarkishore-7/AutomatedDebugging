from debuggingbook.DynamicInvariants import InvariantAnnotator, INVARIANT_PROPERTIES
import random

def mystery(x, y):
    if len(y) > 0:
        return x * y
    else:
        raise ValueError('len(y) <= 0')
        

def test_mystery():
    mystery(1, 'test')
    mystery(-1, 'test')
    
INVARIANT_PROPERTIES += ["isinstance(Y,str)", "len(Y)>0"]
def run() -> InvariantAnnotator:
    with InvariantAnnotator () as annotator:
        test_mystery()
    return annotator


if __name__ == '__main__':
    print(run().function_with_invariants('mystery'))
