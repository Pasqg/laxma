import logging
from functools import singledispatch

from itertools import islice

from examples.lisp.constructs import Form, builtin_functions, to_object, is_function_def, is_import, to_function, \
    Function, Atom
from parser.ast import AST

logger = logging.getLogger("quokko.compiler")


def compile_args(ast: AST):
    return ", ".join(compile_obj(child) for child in islice(ast.children, 1, len(ast.children)))


@singledispatch
def compile_obj(obj, indent: int = 0):
    raise TypeError(f"Could not compile object {obj}")


@compile_obj.register
def _(obj: Atom, indent: int = 0):
    current_indent = ' ' * (indent * 4)
    return f"{current_indent}{obj.value}"


@compile_obj.register
def _(obj: Form, indent: int = 0):
    current_indent = ' ' * (indent * 4)
    builtins = builtin_functions()

    if not obj.elements:
        return ""
    if not isinstance(obj.elements[0], Atom):
        raise SyntaxError(f"Expected Atom as first element of Form, but got {obj.elements[0]}")

    form_name = obj.elements[0].value
    if form_name in builtins:
        return f"{current_indent}{compile_builtin(obj)}"
    else:
        args = ','.join([compile_obj(element) for element in islice(obj.elements, 1, len(obj.elements))])
        return f"{current_indent}{form_name}({args})"


def compile_builtin(form: Form):
    function_name = form.elements[0].value

    def create_body(delim, elements: islice | list = islice(form.elements, 1, len(form.elements))):
        return delim.join([compile_obj(element) for element in elements])

    match function_name:
        case "import":
            return f"import {form.elements[1].value}"
        case "print":
            return f"print({create_body(',')})"
        case "+":
            return create_body('+')
        case "-":
            return create_body('-')
        case "*":
            return create_body('*')
        case "/":
            return create_body('/')
    return ""


def compile_function(function: Function, indent: int):
    builtins = builtin_functions()
    if function.name in builtins:
        logger.error(f"Error: builtin function {function.name} is being redefined.")

    def create_body(add_return: bool):
        return_f = lambda i: 'return ' if add_return and i == len(function.body) - 1 else ''
        total_indent = ' ' * (indent + 1) * 4
        body = [f"{total_indent}{return_f(i)}{compile_obj(obj, indent)}" for i, obj in enumerate(function.body)]
        return '\n'.join(body)

    if function.name == "main":
        output = f"if __name__ == '__main__':\n{create_body(False)}\n"
    else:
        output = f"def {function.name}({', '.join(function.args)}):\n{create_body(True)}"

    return output + "\n"


def compile_program(ast: AST) -> tuple[bool, str]:
    if not ast.children:
        return True, ""

    objects = [to_object(child) for child in ast.children]
    for obj in objects:
        if not isinstance(obj, Form):
            return False, f"Got unexpected object at root-level: {obj}"
        if not is_function_def(obj) and is_import(obj):
            return False, f"Expected only function definitions and imports at root-level but got: {obj}"

    functions = {form.elements[1].value: to_function(form) for form in objects if is_function_def(form)}

    # todo should be limited to the entry point file
    if 'main' not in functions:
        return False, f"Function 'main' is not defined!"

    output = ""
    for function in functions.values():
        output += compile_function(function, 0) + "\n"

    return True, output
