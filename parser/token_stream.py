from typing import Self, List, Tuple


class TokenStream[TokenType]:
    def __init__(self, tokens: List[TokenType], start: int = 0):
        self.__tokens = tokens
        self.__start = start

    def __bool__(self) -> bool:
        return self.__start < len(self.tokens)

    def __repr__(self):
        return f"TokenStream({self.tokens})"

    def advance(self) -> Tuple[TokenType, Self]:
        return self.tokens[self.__start], TokenStream(self.tokens, self.__start + 1)

    @property
    def tokens(self):
        return self.__tokens

    def __eq__(self, other):
        return self.__start == other.__start and self.__tokens == other.__tokens
