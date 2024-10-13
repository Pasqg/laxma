from functools import singledispatch

from examples.lisp.constructs import Function, Form, Atom, builtin_functions
from examples.lisp.type_system.types import PrimitiveType, UnrecognizedType, EmptyList, ListType, PossibleEmptyList


@singledispatch
def infer_type(obj, namespace: dict[str, object]) -> tuple[bool, dict[object]]:
    raise TypeError(f"Cannot infer type of {obj}")


@infer_type.register
def _(atom: Atom, namespace: dict[str, object]) -> tuple[bool, PrimitiveType | UnrecognizedType]:
    if isinstance(atom.value, str):
        if atom.value == "\"\"" or (atom.value.startswith("\"") and atom.value.endswith("\"")):
            return True, PrimitiveType.String
        if atom.value in namespace:
            return True, namespace[atom.value]
        try:
            float(atom.value)
            return True, PrimitiveType.Number
        except:
            try:
                int(atom.value)
                return True, PrimitiveType.Number
            except:
                return False, f"Cannot infer type of '{atom.value}'"
    if isinstance(atom.value, int) or isinstance(atom.value, float):
        return True, PrimitiveType.Number
    return False, UnrecognizedType()


@infer_type.register
def _(form: Form, namespace: dict[str, object]) -> tuple[bool, object]:
    elements = form.elements
    first_element = elements[0]
    if isinstance(first_element, Atom):
        name = first_element.value
        if name in namespace:
            return True, namespace[name]
        elif name in builtin_functions():
            match name:
                case "list":
                    if len(elements) == 1:
                        return True, EmptyList()
                    else:
                        result, element_type = infer_type(elements[1], namespace)
                        if not result:
                            return False, element_type
                        for i in range(2, len(elements)):
                            result, i_type = infer_type(elements[i], namespace)
                            if not result or i_type != element_type:
                                return False, f"List {i-1}-th element has type '{i_type.name()}' but expected '{element_type.name()}'"
                        return True, ListType(element_type)
                case "++":
                    result_element, element_type = infer_type(elements[1], namespace)
                    result_list, list_type = infer_type(elements[2], namespace)

                    if isinstance(list_type, EmptyList):
                        return True, ListType(element_type)

                    if isinstance(list_type, ListType) or isinstance(list_type, PossibleEmptyList):
                        if list_type.element.is_compatible(element_type):
                            return True, ListType(element_type)

                    return False, f"Cannot append element of type '{element_type.name()}' to '{list_type.name()}'"
                case "first":
                    result, list_type = infer_type(elements[1], namespace)
                    if result and isinstance(list_type, ListType):
                        return True, list_type.element
                    return False, f"'first' expected a non-empty List type but got '{list_type.name()}'"
                case "rest":
                    result, list_type = infer_type(elements[1], namespace)
                    if result and isinstance(list_type, ListType):
                        return True, list_type
                    return False, f"'rest' expected a non-empty List type but got '{list_type.name()}'"
        return False, f"Unrecognized form '{name}', cannot infer type"
