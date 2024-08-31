from typing import TypeVar, Tuple, Callable

from parser.ast import AST
from parser.token_stream import TokenStream

RuleId = TypeVar("RuleId")
TokenType = TypeVar("TokenType")

type ParserResult[RuleId, TokenType] = Tuple[bool, AST[RuleId, TokenType], TokenStream[TokenType]]
type Combinator[RuleId, TokenType] = Callable[[TokenStream[TokenType]], ParserResult[RuleId, TokenType]]
