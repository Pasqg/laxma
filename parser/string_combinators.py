import re
from typing import Optional

from parser.ast import AST
from parser.token_stream import TokenStream
from parser.types import RuleId, Combinator


def match_str(rule_id: Optional[RuleId], s: str) -> Combinator[RuleId, str]:
    def inner(tokens: TokenStream):
        if tokens:
            token, remaining = tokens.advance()
            if token == s:
                return True, AST(rule_id, [token]), remaining
        return False, AST(), tokens

    return inner


def match_regex(rule_id: Optional[RuleId], pattern) -> Combinator[RuleId, str]:
    def inner(tokens: TokenStream):
        if tokens:
            token, remaining = tokens.advance()
            if re.match(pattern, token):
                return True, AST(rule_id, [token]), remaining
        return False, AST(), tokens

    return inner


def lit(s: str) -> Combinator[RuleId, str]:
    return match_str(None, s)


def regex(r) -> Combinator[RuleId, str]:
    return match_regex(None, r)
