from typing import Optional

from parser.ast import AST
from parser.token_stream import TokenStream
from parser.types import RuleId, TokenType, Combinator


def anonymous(combinator: Combinator[RuleId, TokenType], *args, **kwargs) -> Combinator[RuleId, TokenType]:
    return lambda id: combinator(id, *args, **kwargs)


def match_none(id: Optional[RuleId] = None) -> Combinator[RuleId, TokenType]:
    """
        Matches nothing. Used to make it easier to match both empty and non-empty sequences with one rule.
    """

    def inner(tokens: TokenStream[TokenType]):
        return True, AST(id, [], []), tokens

    return inner


def match_any(id: Optional[RuleId] = None, excluded: Optional[TokenType] = None) -> Combinator[RuleId, TokenType]:
    """
        Matches any one token, excluding the 'excluded' token (if provided).
    """

    def inner(tokens: TokenStream):
        if tokens:
            token, remaining = tokens.advance()
            if token is not excluded:
                return True, AST(id, [token]), remaining
        return False, AST(), tokens

    return inner


def and_match(id: Optional[RuleId], *rules: Combinator[RuleId, TokenType]) -> Combinator[RuleId, TokenType]:
    """
        Returns a match if all the input rules match, otherwise it fails (and backtracks).
    """

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


def or_match(id: Optional[RuleId], *rules: Combinator[RuleId, TokenType]) -> Combinator[RuleId, TokenType]:
    """
        Returns a match if any of the input rules match, otherwise it fails (and backtracks).
    """

    def inner(tokens: TokenStream[TokenType]):
        for rule in rules:
            result, matched, remaining = rule(tokens)
            if result:
                return True, AST(id, matched.matched, [matched]), remaining
        return False, AST(), tokens

    return inner


def many(id: Optional[RuleId] = None, *, element: Combinator[RuleId, TokenType],
         delim: Optional[Combinator[RuleId, TokenType]] = None) -> Combinator[RuleId, TokenType]:
    """
        Matches zero or more occurrences of the provided 'element' rule.
        Optionally, matches a delimiter rule between each of the elements.
    """
    return or_match(id, at_least_one(id, element=element, delim=delim), match_none())


def at_least_one(id: Optional[RuleId] = None, *, element: Combinator[RuleId, TokenType],
                 delim: Optional[Combinator[RuleId, TokenType]] = None) -> Combinator[RuleId, TokenType]:
    """
        Matches at least one occurrence of the provided 'element' rule.
        Optionally, matches a delimiter rule between each of the elements.
    """
    if delim is None:
        def inner(tokens):
            remaining = tokens

            result, ematched, remaining = element(remaining)
            if not result:
                return False, AST(), tokens

            result, mmatched, mremaining = at_least_one(id, element=element, delim=delim)(remaining)
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

            result, mmatched, mremaining = at_least_one(id, element=element, delim=delim)(nremaining)
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
