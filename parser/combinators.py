from collections import deque
from typing import Optional

from parser.ast import AST
from parser.token_stream import TokenStream
from parser.types import RuleId, TokenType, Combinator, ParserResult


def match_none(id: Optional[RuleId] = None) -> Combinator[RuleId, TokenType]:
    """
        Matches nothing. Used to make it easier to match both empty and non-empty sequences with one rule.
    """

    def inner(tokens: TokenStream[TokenType]):
        return ParserResult.succeeded(AST(id), tokens)

    return inner


def match_any(id: Optional[RuleId] = None, excluded: Optional[Combinator[RuleId, TokenType]] = None) -> Combinator[
    RuleId, TokenType]:
    """
        Matches any one token, excluding the 'excluded' token (if provided).
    """

    def inner(tokens: TokenStream) -> ParserResult[TokenType]:
        if tokens:
            if excluded is not None:
                result, ast, remaining = excluded(tokens)
                if result:
                    return ParserResult.failed(tokens)
            token, remaining = tokens.advance()
            return ParserResult.succeeded(AST(id, [token]), remaining)
        return ParserResult.failed(tokens)

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
                return ParserResult.failed(tokens)
            matched += rmatched.matched
            children.append(rmatched)
        return ParserResult.succeeded(AST(id, matched, children), remaining)

    return inner


def or_match(id: Optional[RuleId], *rules: Combinator[RuleId, TokenType]) -> Combinator[RuleId, TokenType]:
    """
        Returns a match if any of the input rules match, otherwise it fails (and backtracks).
    """

    def inner(tokens: TokenStream[TokenType]):
        for rule in rules:
            result, matched, remaining = rule(tokens)
            if result:
                return ParserResult.succeeded(AST(id, matched.matched, [matched]), remaining)
        return ParserResult.failed(tokens)

    return inner


def optional(id: Optional[RuleId] = None, *, parser: Combinator[RuleId, TokenType]) -> Combinator[RuleId, TokenType]:
    return or_match(id, parser, match_none())


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
    first_element = element
    if delim is not None:
        element = and_match(id, delim, element)

    def inner(tokens):
        element_result, element_ast, element_remaining = first_element(tokens)
        if not element_result:
            return ParserResult.failed(tokens)

        stack = deque([(element_result, AST(id, element_ast.matched, [element_ast]), element_remaining)])
        while stack:
            result, ast, remaining = stack.pop()

            element_result, element_ast, element_remaining = element(remaining)
            if element_result:
                if delim is None:
                    stack.append(ParserResult.succeeded(ast.merge(element_ast), element_remaining))
                else:
                    for c in element_ast.children:
                        ast = ast.merge(c)
                    stack.append(ParserResult.succeeded(ast, element_remaining))
            else:
                # If element doesn't match, then return the last result (either no match, or matched until now)
                return ParserResult(result, ast, remaining)

    return inner
