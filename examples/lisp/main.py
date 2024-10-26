import logging.config

from datetime import datetime

from compiler import Compiler
from grammar import lexer, create_parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('lisp-example')

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
        print(ast)

        result, output, _ = Compiler().compile_program(ast)
        if not result:
            logger.error(output)
        else:
            with open("lisp.py", "w") as file:
                file.write(output)
            exec(output)
