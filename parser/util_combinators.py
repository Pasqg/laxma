from parser.ast import AST
from parser.types import Combinator, RuleId, TokenType


def discard(combinator: Combinator[RuleId, TokenType]) -> Combinator[RuleId, TokenType]:
    """
        Discards matched tokens and AST of the input combinator.
        Meant as an optimisation, i.e. can discard boilerplate, comments etc
    """

    def inner(tokens):
        result, _, remaining = combinator(tokens)
        return result, AST(), remaining

    return inner


def ref(combinator: Combinator[RuleId, TokenType]) -> Combinator[RuleId, TokenType]:
    """
        Adds a level of indirection like a reference to allow self/mutual recursive definitions.
        Example: combinator2 = orMath(ref(lambda t: combinator1(t)), match_none)
    """

    def inner(tokens):
        return combinator(tokens)

    return inner
