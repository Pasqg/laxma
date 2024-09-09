def list_create(*args):
    return [x for x in args]


def list_append(lst, *args):
    return lst + list_create(*args)