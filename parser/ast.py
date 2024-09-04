from collections import deque
from typing import List, Optional, Self, Callable


class AST[RuleId, TokenType]:
    def __init__(self,
                 name: Optional[RuleId] = None,
                 matched: Optional[List[TokenType]] = None,
                 children: Optional[List[Self]] = None):
        self.id = name
        self.matched = matched.copy() if matched else []
        self.children = children.copy() if children else []

    def merge(self, other: Optional[Self]):
        if other is not None:
            self.matched += other.matched
            self.children.append(other)
        return self

    def prune(self):
        """
            Prunes the tree by:
                - replacing nodes that have only one child with the child itself.
        """
        children = self.children
        if len(children) == 1:
            child = children[0].prune()
            return AST(self.id, child.matched, child.children)
        return AST(self.id, self.matched, [child.prune() for child in children])

    def __repr__(self):
        results = []

        def visit_fn(node: Self, level: int):
            results.append(f"{'  |' * level}  +- {node.id}: {' '.join(node.matched)}")

        self.__visit__(visit_fn)
        return "\n".join(results)

    def __visit__(self, visit_fn: Callable[[Self, int], None], level: int = 0):
        stack = deque([(self, level)])
        while stack:
            node, level = stack.pop()
            visit_fn(node, level)
            for child in reversed(node.children):
                stack.append((child, level + 1))

    def __eq__(self, other: Self):
        return self.id == other.id and self.matched == other.matched and self.children == other.children
