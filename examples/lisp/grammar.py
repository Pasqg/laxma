from enum import Enum, auto
import re

from parser.combinators import or_match, and_match, many, at_least_one
from parser.string_combinators import regex, lit
from parser.token_stream import TokenStream
from parser.util_combinators import ref


class LispRule(Enum):
    PROGRAM = auto()
    FORM = auto()
    ELEMENTS = auto()
    ELEMENT = auto()

    EMPTY = auto()
    ATOM = auto()
    STRING = auto()
    IDENTIFIER = auto()
    NUMBER = auto()


def create_parser():
    number = regex(r"\d+|\d+\.\d+")
    string = regex(r'"[^"]*"')
    identifier = regex(r"[a-zA-Z\-\+0-9]+")
    atom = or_match(LispRule.ATOM, identifier, number, string)

    element = or_match(LispRule.ELEMENT, ref(lambda t: form(t)), atom)
    form = and_match(LispRule.FORM, lit("("), many(LispRule.ELEMENTS, element=element), lit(")"))

    program = at_least_one(LispRule.PROGRAM, element=form)

    return program


def lexer():
    return lambda text: TokenStream(
        re.findall(r'\d+|\d+\.\d+|[a-zA-Z0-9\-+.]+|/\*|\*/|"[^"]*"|[()]', text))
