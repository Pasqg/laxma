from itertools import islice
from typing import Self
from pydantic import BaseModel

from examples.lisp.grammar import LispRule
from parser.ast import AST


class Atom(BaseModel):
    value: str | int | float


class Form(BaseModel):
    elements: list[Self | Atom]


class EmptyForm:
    pass


class Function(BaseModel):
    name: str
    args: list[str]
    body: list[Form | Atom]


class Program(BaseModel):
    functions: dict[str, Function]


def builtin_functions():
    return {'import',
            '+', '-', 'x', '/', '*',
            '=', '>', '<', '>=', '<=', 'and', 'or', 'not',
            'print', 'list', 'append', 'map', 'first',
            'lambda', 'if'}


def to_object(ast: AST):
    match ast.id.value:
        case LispRule.ELEMENTS.value:
            return [to_object(child) for child in ast.children]
        case LispRule.ATOM.value:
            return Atom(value=ast.matched[0])
        case LispRule.FORM.value:
            return to_form(ast)
    return None


def to_form(ast: AST):
    if ast.children:
        elements = to_object(ast.children[0])
        return Form(elements=elements if isinstance(elements, list) else [elements])
    return EmptyForm()


def to_function(form: Form):
    function_name = form.elements[1].value
    builtins = builtin_functions()
    if function_name in builtins:
        raise SyntaxError(f"Builtin function {function_name} is being redefined.")

    args = [arg.value for arg in form.elements[2].elements]
    return Function(name=function_name, args=args, body=islice(form.elements, 3, len(form.elements)))


def is_function_def(form: Form):
    first_element = form.elements[0]
    return isinstance(first_element, Atom) and first_element.value == 'fun'


def is_import(form: Form):
    first_element = form.elements[0]
    return isinstance(first_element, Atom) and first_element.value == 'import'
