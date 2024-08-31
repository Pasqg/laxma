from typing import Callable, List, Tuple, Optional

from parser.ast import AST
from parser.token_stream import TokenStream
from parser.types import RuleId, TokenType

type ParserResult[RuleId, TokenType] = Tuple[bool, AST[RuleId, TokenType], TokenStream[TokenType]]
type Combinator[RuleId, TokenType] = Callable[[TokenStream[TokenType]], ParserResult[RuleId, TokenType]]


def matchNone(id: RuleId):
    def inner(tokens: TokenStream[TokenType]):
        return True, AST(id, [], []), tokens

    return inner


def andMatch(id: RuleId, *rules: Combinator[RuleId, TokenType]):
    def inner(tokens: TokenStream[TokenType]):
        remaining = tokens
        matched = []
        children = []
        for rule in rules:
            result, rmatched, remaining = rule(remaining)
            if not result:
                return False, AST(), tokens
            matched += rmatched.matched
            children.append(rmatched)
        return True, AST(id, matched, children), remaining

    return inner


def orMatch(id: RuleId, *rules: Combinator[RuleId, TokenType]):
    def inner(tokens: TokenStream[TokenType]):
        for rule in rules:
            result, matched, remaining = rule(tokens)
            if result:
                return True, AST(id, matched.matched, [matched]), remaining
        return False, AST(), tokens

    return inner


def listParser(id: RuleId, *, element: Combinator[RuleId, TokenType],
               delim: Optional[Combinator[RuleId, TokenType]] = None):
    if delim is None:
        def inner(tokens):
            remaining = tokens

            result, ematched, remaining = element(remaining)
            if not result:
                return False, AST(), tokens

            result, mmatched, mremaining = listParser(id, element=element, delim=delim)(remaining)
            if result:
                return (True,
                        AST(id,
                            ematched.matched + mmatched.matched,
                            # Could be flattened to be agnostic of left/right recursion
                            [ematched, mmatched]),
                        mremaining)
            else:
                # matches only element
                return True, AST(id, ematched.matched, [ematched]), remaining
    else:
        def inner(tokens):
            remaining = tokens

            result, ematched, remaining = element(remaining)
            if not result:
                return False, AST(), tokens

            # Handle None for delim better!
            result, nmatched, nremaining = delim(remaining)
            if not result:
                return True, AST(id, ematched.matched, [ematched]), remaining

            result, mmatched, mremaining = listParser(id, element=element, delim=delim)(nremaining)
            if result:
                return (True,
                        AST(id,
                            ematched.matched + nmatched.matched + mmatched.matched,
                            # Could be flattened to be agnostic of left/right recursion
                            [ematched, nmatched, mmatched] if nmatched else [ematched, nmatched]),
                        mremaining)
            else:
                # matches only element
                return True, AST(id, ematched.matched, [ematched]), remaining

    return inner
