import re

from parser.ast import AST
from parser.token_stream import TokenStream
from parser.types import RuleId, TokenType
from parser.combinators import Combinator, ParserResult


def equals(rule_id: RuleId, s: str):
    def inner(tokens: TokenStream):
        if tokens:
            token, remaining = tokens.advance()
            if token == s:
                return True, AST(rule_id, [token]), remaining
        return False, AST(), tokens

    return inner


def pattern(rule_id: RuleId, pattern):
    def inner(tokens: TokenStream):
        if tokens:
            token, remaining = tokens.advance()
            if re.match(pattern, token):
                return True, AST(rule_id, [token]), remaining
        return False, AST(), tokens

    return inner
