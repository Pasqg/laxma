import datetime
from enum import Enum, auto
import re

from parser.combinators import or_match, and_match, many, at_least_one
from parser.string_combinators import regex, lit
from parser.token_stream import TokenStream
from parser.util_combinators import ref


class LispRule(Enum):
    PROGRAM = auto()
    FORM = auto()
    FUNCTION_DEF = auto()
    ELEMENTS = auto()
    ELEMENT = auto()

    EMPTY = auto()
    ATOM = auto()
    STRING = auto()
    IDENTIFIER = auto()
    NUMBER = auto()


def create_parser():
    number = regex(r"\d+|\d+\.\d+")
    string = regex(r'".*"')
    identifier = regex(r"[a-zA-Z\-\+\.0-9]+")
    atom = or_match(LispRule.IDENTIFIER, identifier, number, string)

    element = or_match(LispRule.ELEMENT, ref(lambda t: form(t)), atom)
    form = and_match(LispRule.FORM, lit("("), many(LispRule.ELEMENTS, element=element), lit(")"))

    function_def = and_match(LispRule.FUNCTION_DEF, lit("("), lit("fun"), identifier,
                             form, at_least_one(LispRule.ELEMENTS, element=element), lit(")"))

    program = at_least_one(LispRule.PROGRAM, element=function_def)

    return program


def lexer():
    return lambda text: TokenStream(
        re.findall(r'\d+|\d+\.\d+|[a-zA-Z0-9\-+.]+|/\*|\*/|".*"|[()]', text))


if __name__ == "__main__":
    with open("../resources/lisp.lsp") as file:
        tokens = lexer()(file.read().replace("\n", " "))

    parser = create_parser()

    start = datetime.datetime.now()
    result, ast, remaining = parser(tokens)
    end = datetime.datetime.now()

    print(end - start)

    if not result:
        print("Could not parse!")
    elif remaining:
        print("Could not parse the whole input!")
    else:
        print(ast.prune())
