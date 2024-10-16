from typing import Self, Optional
from pydantic import BaseModel

from examples.lisp.grammar import LispRule
from parser.ast import AST


class Atom(BaseModel):
    value: str | int | float


class Form(BaseModel):
    elements: list[Self | Atom]


class EmptyForm:
    pass


class TypeName(BaseModel):
    base_type: str
    sub_type: Optional[Self]


class TypeDec(BaseModel):
    identifier: str
    type_name: TypeName


class Function(BaseModel):
    name: str
    args: list[TypeDec]
    body: list[Form | Atom]


class Program(BaseModel):
    functions: dict[str, Function]


def builtin_functions():
    return {'import',
            '++', '+', '-', '/', '*', '^',
            '=', '>', '<', '>=', '<=', 'and', 'or', 'not',
            'print', 'list', 'append', 'map', 'filter',
            'first', 'rest', 'lambda', 'if'}


def to_object(ast: AST):
    match ast.id.value:
        case LispRule.ELEMENTS.value:
            return [to_object(child) for child in ast.children]
        case LispRule.ATOM.value:
            return Atom(value=ast.matched[0])
        case LispRule.FORM.value:
            return to_form(ast)
        case LispRule.FUNCTION_DEF.value:
            return to_function(ast)
    return None


def to_form(ast: AST):
    if ast.children:
        elements = to_object(ast.children[0])
        return Form(elements=elements if isinstance(elements, list) else [elements])
    return EmptyForm()


def to_type(ast: AST) -> TypeName:
    base_type = ast.matched[0]
    if ast.children:
        return TypeName(base_type=base_type, sub_type=to_type(ast.children[0]))
    return TypeName(base_type=base_type, sub_type=None)


def to_args(ast: AST) -> list[TypeDec]:
    return [TypeDec(identifier=type_dec.matched[0] if type_dec.id.value == LispRule.TYPE_DEC.value else ast.matched[0],
                    type_name=to_type(
                        type_dec.children[0] if type_dec.id.value == LispRule.TYPE_DEC.value else type_dec))
            for type_dec in ast.children]


def to_function(ast: AST) -> Function:
    function_name = ast.matched[2]
    builtins = builtin_functions()
    if function_name in builtins:
        raise SyntaxError(f"Builtin function {function_name} is being redefined.")

    args = to_args(ast.children[0])
    return Function(name=function_name, args=args, body=[to_object(ast.children[1])])


def is_import(form: Form) -> bool:
    first_element = form.elements[0]
    return isinstance(first_element, Atom) and first_element.value == 'import'
