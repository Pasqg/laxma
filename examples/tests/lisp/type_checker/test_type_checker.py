from examples.lisp.constructs import Atom, Form


from examples.lisp.type_system.type_checker import infer_type
from examples.lisp.type_system.types import PrimitiveType, EmptyList, ListType

EMPTY_LIST = Form(elements=[Atom(value="list")])
STRING = Atom(value="\"123\"")
VAR = Atom(value="x")
NUMBER = Atom(value=123)


def list_of(*forms):
    return Form(elements=[Atom(value="list")] + [form for form in forms])


def test_atom_type_inference():
    assert infer_type(STRING, {}) == (True, PrimitiveType.String)
    assert infer_type(NUMBER, {}) == (True, PrimitiveType.Number)
    assert infer_type(Atom(value=123.456), {}) == (True, PrimitiveType.Number)


def test_list_type_inference():
    assert infer_type(EMPTY_LIST, {}) == (True, EmptyList())
    assert (infer_type(Form(elements=[Atom(value="list"), Atom(value="")]), {})
            == (True, ListType(element=PrimitiveType.String)))
    assert (infer_type(Form(elements=[Atom(value="list"), NUMBER]), {})
            == (True, ListType(element=PrimitiveType.Number)))
    assert (infer_type(Form(elements=[Atom(value="list"), NUMBER, Atom(value=123.23)]), {})
            == (True, ListType(element=PrimitiveType.Number)))
    assert (infer_type(Form(elements=[Atom(value="list"), NUMBER, Atom(value="")]), {})
            == (False, "List 1-th element has type 'string' but expected 'number'"))

    assert (infer_type(Form(elements=[Atom(value="list"), EMPTY_LIST]), {})
            == (True, ListType(element=EmptyList())))

    assert (infer_type(Form(elements=[Atom(value="list"), EMPTY_LIST, EMPTY_LIST]), {})
            == (True, ListType(element=EmptyList())))
    assert (infer_type(
        Form(elements=[Atom(value="list"), Form(elements=[Atom(value="list"), NUMBER]), EMPTY_LIST]), {})
            == (True, ListType(element=EmptyList())))


def test_first_type_inference():
    first_form = Atom(value="first")

    assert (infer_type(Form(elements=[first_form, EMPTY_LIST]), {})
            == (False, "'first' expected a non-empty List type but got 'EmptyList'"))
    assert (infer_type(Form(elements=[first_form, NUMBER]), {})
            == (False, "'first' expected a non-empty List type but got 'number'"))
    assert (infer_type(Form(elements=[first_form, STRING]), {})
            == (False, "'first' expected a non-empty List type but got 'string'"))
    assert (infer_type(Form(elements=[first_form, Form(elements=[Atom(value="list"), NUMBER])]), {})
            == (True, PrimitiveType.Number))
    assert (infer_type(Form(elements=[first_form, Form(elements=[Atom(value="list"), STRING])]), {})
            == (True, PrimitiveType.String))


def test_append_type_inference():
    append_op = Atom(value="++")

    assert (infer_type(Form(elements=[append_op, NUMBER, EMPTY_LIST]), {})
            == (True, ListType(element=PrimitiveType.Number)))
    assert (infer_type(Form(elements=[append_op, STRING, EMPTY_LIST]), {})
            == (True, ListType(element=PrimitiveType.String)))

    assert (infer_type(Form(elements=[append_op, NUMBER, list_of(NUMBER)]), {})
            == (True, ListType(element=PrimitiveType.Number)))
    assert (infer_type(Form(elements=[append_op, STRING, list_of(STRING)]), {})
            == (True, ListType(element=PrimitiveType.String)))

    assert (infer_type(Form(elements=[append_op, list_of(STRING), list_of(list_of(STRING))]), {})
            == (True, ListType(element=ListType(element=PrimitiveType.String))))
    assert (infer_type(Form(elements=[append_op, list_of(STRING), list_of(list_of(STRING))]), {})
            == (True, ListType(element=ListType(element=PrimitiveType.String))))
    assert (infer_type(Form(elements=[append_op, list_of(EMPTY_LIST), list_of(list_of(STRING))]), {})
            == (True, ListType(element=ListType(element=PrimitiveType.String))))

    assert (infer_type(Form(elements=[append_op, NUMBER, NUMBER]), {})
            == (False, "Cannot append element of type 'number' to 'number'"))
    assert (infer_type(Form(elements=[append_op, NUMBER, STRING]), {})
            == (False, "Cannot append element of type 'number' to 'string'"))

    assert (infer_type(
        Form(elements=[append_op, NUMBER, list_of(STRING)]), {})
            == (False, "Cannot append element of type 'number' to 'List<string>'"))
    assert (infer_type(
        Form(elements=[append_op, STRING, list_of(NUMBER)]), {})
            == (False, "Cannot append element of type 'string' to 'List<number>'"))

    assert (infer_type(
        Form(elements=[append_op, NUMBER, list_of(STRING)]), {})
            == (False, "Cannot append element of type 'number' to 'List<string>'"))
