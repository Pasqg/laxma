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
