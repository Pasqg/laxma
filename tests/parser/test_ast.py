from parser.ast import AST
import logging.config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_ast")


def test_pruning():
    ast = AST("variable", [], [AST("identifier", [], [AST("name", ["myvar"])])])

    pruned = ast.prune()
    print(pruned)

    assert pruned == AST("variable", ["myvar"])


def test_pruning_excluded():
    ast = AST("variable", [], [AST("identifier", [], [AST("name", ["myvar"])])])

    pruned = ast.prune(excluded={"variable"})
    print(pruned)

    assert pruned == AST("variable", [], [AST("identifier", ["myvar"], [])])


def test_pruning_use_child_rule():
    ast = AST("variable", [], [AST("identifier", [], [AST("name", ["myvar"])])])

    pruned = ast.prune(excluded={"variable"}, use_child_rule={"identifier"})
    print(pruned)

    assert pruned == AST("variable", [], [AST("name", ["myvar"], [])])
