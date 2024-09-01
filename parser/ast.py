from typing import List, Optional, Self


class AST[RuleId, TokenType]:
    def __init__(self,
                 name: Optional[RuleId] = None,
                 matched: Optional[List[TokenType]] = None,
                 children: Optional[List[Self]] = None):
        self.name = name
        self.matched = matched.copy() if matched else []
        self.children = children.copy() if children else []

    def merge(self, other: Optional[Self]):
        if other is not None:
            self.matched += other.matched
            self.children.append(other)
        return self

    def __repr__(self):
        return f"AST({self.name}, {self.matched}, {self.children})"

    def __eq__(self, other):
        return self.name == other.name and self.matched == other.matched and self.children == other.children
