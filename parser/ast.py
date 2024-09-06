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

    def prune(self, *, excluded: set[RuleId] = None, use_child_rule: set[RuleId] = None):
        """
            Prunes the tree depth-first by:
                - replacing nodes that have only one child with the child itself (i.e. degenerate subtree)
                - removing nodes with None id and no children (structural tokens that provide no additional information)

            Example:
                Unpruned: variable -> identifier -> name ["myvar"]
                Pruned: variable ["myvar"]

            Use the excluded set to exclude rules from being pruned. Note this does not apply recursively.
            Example:
                excluded = {"variable"}
                Unpruned: variable -> identifier -> name ["myvar"]
                Pruned: variable -> identifier ["myvar"]

            The parent rule is used for the child's matched tokens unless use_child_rule contains the parent rule.
            Note this doesn't apply recursively.
            Example: use_child_rule
                excluded = {"variable"} use_child_rule = {"Identifier"}
                Unpruned: variable -> identifier -> name ["myvar"]
                Pruned: variable -> name ["myvar"]
        """
        if excluded is None:
            excluded = {}
        if use_child_rule is None:
            use_child_rule = {}

        children = self.children
        if len(children) == 1 and self.id not in excluded:
            child = children[0]
            if child.id is None:
                return AST(self.id, child.matched)
            child = child.prune(excluded=excluded, use_child_rule=use_child_rule)

            rule_id = self.id
            if self.id is None or self.id in use_child_rule:
                rule_id = child.id
            return AST(rule_id, child.matched, child.children)
        return AST(self.id, self.matched,
                   [child.prune(excluded=excluded, use_child_rule=use_child_rule) for child in children if
                    child.id is not None or len(child.children) > 1])

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
