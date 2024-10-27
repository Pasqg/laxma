from examples.lisp.type_system.types import PrimitiveType, EmptyList, ListType, PossibleEmptyList, UnrecognizedType


def test_unrecognized_type():
    assert not PrimitiveType.Number.is_compatible(UnrecognizedType())
    assert not PrimitiveType.String.is_compatible(UnrecognizedType())
    assert not EmptyList().is_compatible(UnrecognizedType())
    assert not ListType(EmptyList()).is_compatible(UnrecognizedType())
    assert not ListType(PrimitiveType.String).is_compatible(UnrecognizedType())

    assert not UnrecognizedType().is_compatible(PrimitiveType.Number)
    assert not UnrecognizedType().is_compatible(PrimitiveType.String)
    assert not UnrecognizedType().is_compatible(UnrecognizedType())
    assert not UnrecognizedType().is_compatible(ListType(EmptyList()))
    assert not UnrecognizedType().is_compatible(ListType(PrimitiveType.String))


def test_primitive_type_compatibility():
    assert PrimitiveType.Number.is_compatible(PrimitiveType.Number)
    assert PrimitiveType.String.is_compatible(PrimitiveType.String)

    assert not PrimitiveType.Number.is_compatible(PrimitiveType.String)
    assert not PrimitiveType.String.is_compatible(PrimitiveType.Number)


def test_list_types_compatibility():
    assert EmptyList().is_compatible(EmptyList())
    assert ListType(PrimitiveType.Number).is_compatible(ListType(PrimitiveType.Number))
    assert ListType(PrimitiveType.String).is_compatible(ListType(PrimitiveType.String))
    assert PossibleEmptyList(PrimitiveType.Number).is_compatible(PossibleEmptyList(PrimitiveType.Number))
    assert PossibleEmptyList(PrimitiveType.String).is_compatible(PossibleEmptyList(PrimitiveType.String))

    assert EmptyList().is_compatible(ListType(PrimitiveType.Number))
    assert EmptyList().is_compatible(ListType(PrimitiveType.String))
    assert EmptyList().is_compatible(PossibleEmptyList(PrimitiveType.Number))
    assert EmptyList().is_compatible(PossibleEmptyList(PrimitiveType.String))
    assert ListType(PrimitiveType.Number).is_compatible(EmptyList())
    assert ListType(PrimitiveType.String).is_compatible(EmptyList())
    assert PossibleEmptyList(PrimitiveType.Number).is_compatible(EmptyList())
    assert PossibleEmptyList(PrimitiveType.String).is_compatible(EmptyList())


def test_type_names():
    assert PrimitiveType.String.name() == "string"
    assert PrimitiveType.Number.name() == "number"
    assert EmptyList().name() == "EmptyList"
    assert ListType(PrimitiveType.String).name() == "List[string]"
    assert ListType(PrimitiveType.Number).name() == "List[number]"
    assert ListType(EmptyList()).name() == "List[EmptyList]"
