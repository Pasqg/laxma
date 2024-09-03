from typing import TypeVar, Tuple, Callable

from parser.ast import AST
from parser.token_stream import TokenStream

RuleId = TypeVar("RuleId")
TokenType = TypeVar("TokenType")

type Combinator[RuleId, TokenType] = Callable[[TokenStream[TokenType]], ParserResult[TokenType]]


class ParserResult[TokenType]:
    def __init__(self, result: bool, ast: AST, remaining: TokenStream[TokenType]):
        self.__result__ = result
        self.__ast__ = ast
        self.__remaining__ = remaining

    def __iter__(self):
        return iter((self.__result__, self.__ast__, self.__remaining__))

    def __bool__(self):
        return self.__result__

    @staticmethod
    def failed(remaining: TokenStream[TokenType]):
        return ParserResult(False, AST(), remaining)

    @staticmethod
    def succeeded(ast: AST, remaining: TokenStream[TokenType]):
        return ParserResult(True, ast, remaining)

    def __eq__(self, other):
        return self.__result__ == other.__result__ and self.__ast__ == other.__ast__ and self.__remaining__ == other.__remaining__
