from enum import Enum


class UnrecognizedType:
    def name(self):
        return "UnrecognizedType"

    def is_compatible(self, other_type):
        return False


class PrimitiveType(Enum):
    Number = "number"
    String = "string"

    def name(self):
        return self.value

    def is_compatible(self, other_type):
        if isinstance(other_type, PrimitiveType):
            return self.value == other_type.value
        return False


class EmptyList:
    def name(self):
        return "EmptyList"

    def is_compatible(self, other_type):
        return (isinstance(other_type, EmptyList)
                or isinstance(other_type, ListType)
                or isinstance(other_type, PossibleEmptyList))


class ListType:
    def __init__(self, element):
        self.element = element

    def name(self):
        return "List"

    def is_compatible(self, other_type):
        if isinstance(other_type, EmptyList):
            return True

        if isinstance(other_type, ListType) or isinstance(other_type, PossibleEmptyList):
            return self.element.is_compatible(other_type.element)

        return False


class PossibleEmptyList:
    def __init__(self, element):
        self.element = element

    def name(self):
        return "PossibleEmptyList"

    def is_compatible(self, other_type):
        if isinstance(other_type, EmptyList):
            return True

        if isinstance(other_type, ListType) or isinstance(other_type, PossibleEmptyList):
            return self.element.is_compatible(other_type.element)

        return False
