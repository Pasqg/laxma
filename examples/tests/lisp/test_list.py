from examples.lisp.lisp_core import list_create, list_append


def test_create():
    assert list_create() == []
    assert list_create(1) == [1]
    assert list_create(1, 2) == [1, 2]


def test_append():
    assert list_append(1, []) == [1]
    assert list_append(2, [1]) == [1, 2]
    assert list_append(3, [1, 2]) == [1, 2, 3]
    assert list_append(4, [1, 2, 3]) == [1, 2, 3, 4]
