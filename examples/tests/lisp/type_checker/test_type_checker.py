from examples.lisp.constructs import Atom, Form

from examples.lisp.type_system.type_checker import infer_type, infer_element_types
from examples.lisp.type_system.types import PrimitiveType, EmptyList, ListType, PossibleEmptyList

EMPTY_LIST = Form(elements=[Atom(value="list")])
STRING = Atom(value="\"123\"")
VAR = Atom(value="x")
NUMBER = Atom(value=123)
BOOL = Atom(value="false")


def list_of(*forms):
    return Form(elements=[Atom(value="list")] + [form for form in forms])


def test_bool_type_inference():
    assert infer_type(Atom(value="false"), {}) == (True, PrimitiveType.Bool)
    assert infer_type(Atom(value="true"), {}) == (True, PrimitiveType.Bool)


def test_atom_type_inference():
    assert infer_type(STRING, {}) == (True, PrimitiveType.String)
    assert infer_type(Atom(value="\"\""), {}) == (True, PrimitiveType.String)
    assert infer_type(NUMBER, {}) == (True, PrimitiveType.Number)
    assert infer_type(Atom(value=123.456), {}) == (True, PrimitiveType.Number)


def test_element_type_inference():
    assert infer_element_types(PrimitiveType.Number, PrimitiveType.Number) == (True, PrimitiveType.Number)
    assert infer_element_types(PrimitiveType.String, PrimitiveType.String) == (True, PrimitiveType.String)
    assert infer_element_types(EmptyList(), EmptyList()) == (True, EmptyList())
    assert (infer_element_types(ListType(PrimitiveType.Number), ListType(PrimitiveType.Number))
            == (True, ListType(PrimitiveType.Number)))
    assert (infer_element_types(ListType(ListType(PrimitiveType.Number)), ListType(ListType(PrimitiveType.Number)))
            == (True, ListType(ListType(PrimitiveType.Number))))

    assert (infer_element_types(EmptyList(), ListType(PrimitiveType.Number))
            == (True, PossibleEmptyList(element=PrimitiveType.Number)))
    assert (infer_element_types(ListType(PrimitiveType.Number), EmptyList())
            == (True, PossibleEmptyList(element=PrimitiveType.Number)))
    assert (infer_element_types(EmptyList(), ListType(ListType(PrimitiveType.Number)))
            == (True, PossibleEmptyList(element=ListType(PrimitiveType.Number))))
    assert (infer_element_types(ListType(ListType(PrimitiveType.Number)), EmptyList())
            == (True, PossibleEmptyList(element=ListType(PrimitiveType.Number))))

    assert (infer_element_types(ListType(ListType(PrimitiveType.Number)), ListType(EmptyList()))
            == (True, ListType(PossibleEmptyList(element=PrimitiveType.Number))))
    assert (infer_element_types(ListType(EmptyList()), ListType(ListType(PrimitiveType.Number)))
            == (True, ListType(PossibleEmptyList(element=PrimitiveType.Number))))

    assert (infer_element_types(ListType(ListType(PrimitiveType.Number)),
                                ListType(PossibleEmptyList(element=PrimitiveType.Number)))
            == (True, ListType(PossibleEmptyList(element=PrimitiveType.Number))))
    assert (infer_element_types(ListType(PossibleEmptyList(element=PrimitiveType.Number)),
                                ListType(ListType(PrimitiveType.Number)))
            == (True, ListType(PossibleEmptyList(element=PrimitiveType.Number))))

    assert (infer_element_types(PrimitiveType.Number, PrimitiveType.String)
            == (False, "Incompatible list types 'number' and 'string'"))
    assert (infer_element_types(ListType(PrimitiveType.Number), ListType(PrimitiveType.String))
            == (False, "Incompatible list types 'List<number>' and 'List<string>'"))
    assert (infer_element_types(ListType(ListType(PrimitiveType.String)),
                                ListType(ListType(PrimitiveType.Number)))
            == (False, "Incompatible list types 'List<List<string>>' and 'List<List<number>>'"))


def test_list_type_inference():
    assert infer_type(EMPTY_LIST, {}) == (True, EmptyList())
    assert (infer_type(list_of(STRING), {})
            == (True, ListType(PrimitiveType.String)))
    assert (infer_type(list_of(NUMBER), {})
            == (True, ListType(PrimitiveType.Number)))
    assert (infer_type(list_of(NUMBER, Atom(value=123.23)), {})
            == (True, ListType(PrimitiveType.Number)))

    assert (infer_type(list_of(EMPTY_LIST), {})
            == (True, ListType(EmptyList())))
    assert (infer_type(list_of(EMPTY_LIST, EMPTY_LIST), {})
            == (True, ListType(EmptyList())))
    assert (infer_type(list_of(list_of(NUMBER), EMPTY_LIST), {})
            == (True, ListType(PossibleEmptyList(element=PrimitiveType.Number))))

    assert (infer_type(list_of(list_of(list_of(NUMBER)), list_of(list_of(NUMBER), EMPTY_LIST)), {})
            == (True, ListType(ListType(PossibleEmptyList(element=PrimitiveType.Number)))))
    assert (infer_type(
        list_of(list_of(EMPTY_LIST), EMPTY_LIST, list_of(EMPTY_LIST, list_of(list_of(EMPTY_LIST, EMPTY_LIST)))), {})
            == (True,
                ListType(PossibleEmptyList(element=PossibleEmptyList(element=ListType(EmptyList()))))))

    assert (infer_type(list_of(NUMBER, STRING), {})
            == (False, "List 1-th element has type 'string' which is not compatible with inferred type 'number'"))
    assert (infer_type(list_of(list_of(NUMBER), list_of(STRING)), {})
            == (False,
                "List 1-th element has type 'List<string>' which is not compatible with inferred type 'List<number>'"))


def test_first_type_inference():
    first_form = Atom(value="first")

    assert (infer_type(Form(elements=[first_form, EMPTY_LIST]), {})
            == (False, "'first' expected a non-empty List type but got 'EmptyList'"))
    assert (infer_type(Form(elements=[first_form, NUMBER]), {})
            == (False, "'first' expected a non-empty List type but got 'number'"))
    assert (infer_type(Form(elements=[first_form, STRING]), {})
            == (False, "'first' expected a non-empty List type but got 'string'"))
    assert (infer_type(Form(elements=[first_form, list_of(NUMBER)]), {})
            == (True, PrimitiveType.Number))
    assert (infer_type(Form(elements=[first_form, list_of(STRING)]), {})
            == (True, PrimitiveType.String))
    assert (infer_type(Form(elements=[first_form, list_of(list_of(NUMBER))]), {})
            == (True, ListType(PrimitiveType.Number)))


def test_rest_type_inference():
    first_form = Atom(value="rest")

    assert (infer_type(Form(elements=[first_form, EMPTY_LIST]), {})
            == (False, "'rest' expected a non-empty List type but got 'EmptyList'"))
    assert (infer_type(Form(elements=[first_form, NUMBER]), {})
            == (False, "'rest' expected a non-empty List type but got 'number'"))
    assert (infer_type(Form(elements=[first_form, STRING]), {})
            == (False, "'rest' expected a non-empty List type but got 'string'"))
    assert (infer_type(Form(elements=[first_form, list_of(NUMBER)]), {})
            == (True, PossibleEmptyList(element=PrimitiveType.Number)))
    assert (infer_type(Form(elements=[first_form, list_of(STRING)]), {})
            == (True, PossibleEmptyList(element=PrimitiveType.String)))
    assert (infer_type(Form(elements=[first_form, list_of(list_of(NUMBER))]), {})
            == (True, PossibleEmptyList(element=ListType(PrimitiveType.Number))))


def test_append_type_inference():
    append_op = Atom(value="++")

    assert (infer_type(Form(elements=[append_op, NUMBER, EMPTY_LIST]), {})
            == (True, ListType(PrimitiveType.Number)))
    assert (infer_type(Form(elements=[append_op, STRING, EMPTY_LIST]), {})
            == (True, ListType(PrimitiveType.String)))

    assert (infer_type(Form(elements=[append_op, NUMBER, list_of(NUMBER)]), {})
            == (True, ListType(PrimitiveType.Number)))
    assert (infer_type(Form(elements=[append_op, STRING, list_of(STRING)]), {})
            == (True, ListType(PrimitiveType.String)))

    assert (infer_type(Form(elements=[append_op, EMPTY_LIST, list_of(list_of(STRING))]), {})
            == (True, ListType(PossibleEmptyList(element=PrimitiveType.String))))

    assert (infer_type(Form(elements=[append_op, list_of(STRING), list_of(list_of(STRING))]), {})
            == (True, ListType(ListType(PrimitiveType.String))))
    assert (infer_type(Form(elements=[append_op, list_of(STRING), list_of(list_of(STRING))]), {})
            == (True, ListType(ListType(PrimitiveType.String))))
    assert (infer_type(Form(elements=[append_op, list_of(EMPTY_LIST), list_of(list_of(STRING))]), {})
            == (False, "Cannot append element of type 'List<EmptyList>' to 'List<List<string>>'"))

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

    assert (infer_type(Form(elements=[append_op, EMPTY_LIST, list_of(STRING)]), {})
            == (False, "Cannot append element of type 'EmptyList' to 'List<string>'"))


def test_if_type_inference():
    if_op = Atom(value="if")

    assert (infer_type(Form(elements=[if_op, NUMBER, NUMBER, NUMBER]), {})
            == (False, f"Expected if condition to have type 'bool' but got 'number'"))
    assert (infer_type(Form(elements=[if_op, BOOL, EMPTY_LIST, NUMBER]), {})
            == (False, f"Incompatible types in if branches: 'EmptyList' and 'number'"))
    assert (infer_type(Form(elements=[if_op, BOOL, NUMBER, EMPTY_LIST]), {})
            == (False, f"Incompatible types in if branches: 'number' and 'EmptyList'"))
    assert (infer_type(Form(elements=[if_op, BOOL, NUMBER, list_of(NUMBER)]), {})
            == (False, f"Incompatible types in if branches: 'number' and 'List<number>'"))
    assert (infer_type(Form(elements=[if_op, BOOL, list_of(STRING), list_of(NUMBER)]), {})
            == (False, f"Incompatible types in if branches: 'List<string>' and 'List<number>'"))
    assert (infer_type(Form(elements=[if_op, BOOL, list_of(EMPTY_LIST), list_of(list_of(NUMBER))]), {})
            == (False, f"Incompatible types in if branches: 'List<EmptyList>' and 'List<List<number>>'"))

    assert (infer_type(Form(elements=[if_op, BOOL, NUMBER, NUMBER]), {})
            == (True, PrimitiveType.Number))
    assert (infer_type(Form(elements=[if_op, BOOL, list_of(NUMBER), list_of(NUMBER)]), {})
            == (True, ListType(PrimitiveType.Number)))
    assert (infer_type(Form(elements=[if_op, BOOL, list_of(list_of(NUMBER)), list_of(list_of(NUMBER))]), {})
            == (True, ListType(ListType(PrimitiveType.Number))))
    assert (infer_type(Form(elements=[if_op, BOOL, EMPTY_LIST, EMPTY_LIST]), {})
            == (True, EmptyList()))

    assert (infer_type(Form(elements=[if_op, BOOL, list_of(NUMBER), EMPTY_LIST]), {})
            == (True, PossibleEmptyList(element=PrimitiveType.Number)))
