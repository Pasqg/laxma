from enum import Enum


class UnrecognizedType:
    def name(self):
        return "UnrecognizedType"

    def is_compatible(self, other_type):
        return False

    def __eq__(self, other):
        return isinstance(other, UnrecognizedType)


class PrimitiveType(Enum):
    Number = "number"
    String = "string"
    Bool = "bool"
    Void = "void"

    def name(self):
        return self.value

    def is_compatible(self, other_type):
        if isinstance(other_type, PrimitiveType):
            return self.value == other_type.value
        return False

    def __repr__(self):
        return self.name()

    def __eq__(self, other):
        return isinstance(other, PrimitiveType) and self.value == other.value


class EmptyList:
    def name(self):
        return "EmptyList"

    def is_compatible(self, other_type):
        return (isinstance(other_type, EmptyList)
                or isinstance(other_type, ListType)
                or isinstance(other_type, PossibleEmptyList))

    def __repr__(self):
        return self.name()

    def __eq__(self, other):
        return isinstance(other, EmptyList)


class ListType:
    def __init__(self, element):
        self.element = element

    def name(self):
        return f"List<{self.element.name()}>"

    def is_compatible(self, other_type):
        if isinstance(other_type, EmptyList):
            return True

        if isinstance(other_type, ListType) or isinstance(other_type, PossibleEmptyList):
            return self.element.is_compatible(other_type.element)

        return False

    def __repr__(self):
        return self.name()

    def __eq__(self, other):
        return isinstance(other, ListType) and self.element == other.element


class PossibleEmptyList:
    def __init__(self, element):
        self.element = element

    def name(self):
        return f"PossibleEmptyList<{self.element.name()}>"

    def is_compatible(self, other_type):
        if isinstance(other_type, EmptyList):
            return True

        if isinstance(other_type, ListType) or isinstance(other_type, PossibleEmptyList):
            return self.element.is_compatible(other_type.element)

        return False

    def __repr__(self):
        return self.name()

    def __eq__(self, other):
        return isinstance(other, PossibleEmptyList) and self.element == other.element


builtin_base_types = {
    'number': PrimitiveType.Number,
    'string': PrimitiveType.String,
    'bool': PrimitiveType.Bool,
    'EmptyList': EmptyList(),
}

builtin_types = {
    'List': lambda x: ListType(element=x),
    'List*': lambda x: PossibleEmptyList(element=x),
}
