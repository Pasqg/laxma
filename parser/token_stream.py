from typing import Self, List, Tuple


class TokenStream[TokenType]:
    def __init__(self, tokens: List[TokenType], start: int = 0):
        self.tokens = tokens
        self.start = start

    def __bool__(self) -> bool:
        return self.start < len(self.tokens)

    def __repr__(self):
        return f"TokenStream({self.tokens})"

    def advance(self) -> Tuple[TokenType, Self]:
        return self.tokens[self.start], TokenStream(self.tokens, self.start + 1)
