from datetime import datetime

from compiler import Compiler
from grammar import create_parser, lexer

import traceback

FUNCTIONS = "functions"

PRINT_EXECUTION_TIME = "print_execution_time"

PRINT_AST = "print_ast"


def is_command(user_input: str):
    return user_input and user_input[0] == '/'


def execute_command(user_input: str, env):
    command = user_input[1:]
    match command:
        case "ast":
            enable_toggle(env, PRINT_AST, "AST display")
        case "time":
            enable_toggle(env, PRINT_EXECUTION_TIME, "execution time display")
        case "functions":
            print([f for f in env[FUNCTIONS].keys()])
        case _:
            print(f"ERROR: unrecognised command {command}")


def enable_toggle(env, toggle_name, toggle_display=""):
    env[toggle_name] = not env[toggle_name]
    print(f"{"Enabled" if env[toggle_name] else "Disabled"} {toggle_display}")


def execute(tokens, env, glob):
    result, ast, remaining = parser(tokens)
    if not result:
        print("ERROR: Could not parse!")
    elif remaining:
        print("ERROR: Could not parse the whole input!")
    else:
        if env["print_ast"]:
            print(ast)

        result, output, functions = Compiler().compile_program(ast, env[FUNCTIONS], True)
        if not result:
            print(f"ERROR: {output}")
        else:
            env[FUNCTIONS] = {
                **env[FUNCTIONS],
                **functions,
            }

            with open("lisp.py", "w") as file:
                file.write(output)

            start = datetime.now()
            exec(output, glob)
            if env[PRINT_EXECUTION_TIME]:
                print(f"Executed in {datetime.now() - start}")


if __name__ == "__main__":
    glob = {}
    environment = {
        PRINT_AST: True,
        PRINT_EXECUTION_TIME: True,
        FUNCTIONS: {}
    }

    parser = create_parser()
    lexer = lexer()

    while True:
        user_form = input("lisp> ")

        if is_command(user_form):
            execute_command(user_form, environment)
        else:
            tokens = lexer(user_form.replace("\n", " "))

            try:
                execute(tokens, environment, glob)
            except Exception as e:
                print(traceback.format_exc())
