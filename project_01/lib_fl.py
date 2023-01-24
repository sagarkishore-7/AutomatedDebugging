import atexit
import pickle

data = dict()


def dump_data():
    with open('dump', 'wb') as fp:
        pickle.dump(data, fp)


atexit.register(dump_data)
