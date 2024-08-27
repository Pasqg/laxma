from typing import List, Optional, Self


class AST[RuleId, TokenType]:
    def __init__(self,
                 name: Optional[RuleId] = None,
                 matched: Optional[List[TokenType]] = None,
                 children: Optional[List[Self]] = None):
        self.name = name
        self.matched = matched if matched else []
        self.children = children if children else []

    def __repr__(self):
        return f"AST({self.name}, {self.matched}, '{' '.join(n.name for n in self.children)}')"
