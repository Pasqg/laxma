from random import Random


def list_create(*args):
    return [x for x in args]


def list_append(value, lst):
    return lst + [value]


def randval():
    return Random().random()