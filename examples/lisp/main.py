import logging.config

from datetime import datetime

from examples.lisp.grammar import lexer, create_parser, LispRule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('quokko')

if __name__ == "__main__":
    with open("../resources/lisp.lsp") as file:
        tokens = lexer()(file.read().replace("\n", " "))

    parser = create_parser()

    start = datetime.now()
    result, ast, remaining = parser(tokens)
    logger.info(datetime.now() - start)

    if not result:
        logger.error("Could not parse!")
    elif remaining:
        logger.error("Could not parse the whole input!")
    else:
        pruned = ast.prune(excluded={}, use_child_rule={LispRule.ELEMENT})
        logger.info(pruned)