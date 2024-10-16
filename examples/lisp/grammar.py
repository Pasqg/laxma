from enum import Enum, auto
import re

from parser.combinators import or_match, and_match, many, at_least_one, Combinator
from parser.string_combinators import regex, lit
from parser.token_stream import TokenStream
from parser.types import ParserResult
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


STANDALONE_TOKENS = {
    'number': r"\d+|\d+\.\d+",
    'string': r'"[^"]*"',
    'identifier': r"[a-zA-Z\-\+\*/0-9<>=]+",
    'parenthesis': "[()]"
}


def create_parser() -> Combinator[TokenStream, ParserResult]:
    number = regex(STANDALONE_TOKENS['number'])
    string = regex(STANDALONE_TOKENS['string'])
    identifier = regex(STANDALONE_TOKENS['identifier'])
    atom = or_match(LispRule.ATOM, identifier, number, string)

    element = or_match(LispRule.ELEMENT, ref(lambda t: form(t)), atom)
    form = and_match(LispRule.FORM, lit("("), many(LispRule.ELEMENTS, element=element), lit(")"))

    program = at_least_one(LispRule.PROGRAM, element=form)

    program = at_least_one(LispRule.PROGRAM, element=form)

    def pruner(tokens: TokenStream) -> ParserResult:
        result, ast, remaining = program(tokens)
        return ParserResult(result,
                            ast.prune(excluded={LispRule.PROGRAM},
                                      use_child_rule={LispRule.ELEMENT, LispRule.ELEMENTS}),
                            remaining)

    return pruner


def lexer():
    return lambda text: TokenStream(re.findall('|'.join(STANDALONE_TOKENS.values()), text))
