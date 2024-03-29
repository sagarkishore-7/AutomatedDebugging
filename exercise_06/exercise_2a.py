from debuggingbook.DynamicInvariants import TypeAnnotator


def mystery(x, y):
    if len(y) > 0:
        return x * y
    else:
        raise ValueError('len(y) <= 0')
        

def test_mystery():
    mystery(1, 'test')
    mystery(-1, 'test')
    

def run() -> TypeAnnotator:
    with TypeAnnotator() as ann:
        test_mystery()
    return ann


if __name__ == '__main__':
    print(run().typed_function('mystery'))
