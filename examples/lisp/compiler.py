import logging
from functools import singledispatch, singledispatchmethod

from itertools import islice

from examples.lisp.constructs import Form, builtin_functions, to_object, Function, Atom
from examples.lisp.type_system.type_checker import check_types, infer_type
from parser.ast import AST

logger = logging.getLogger("laxma.compiler")

class Compiler:
    @singledispatchmethod
    def compile_obj(self, obj, indent: int = 0):
        raise TypeError(f"Could not compile object {obj}")


    @compile_obj.register
    def _(self, obj: Atom, indent: int = 0):
        current_indent = ' ' * (indent * 4)
        value = obj.value
        if obj.value == 'true' or obj.value == 'false':
            value = obj.value.capitalize()
        return f"{current_indent}{value}"


    @compile_obj.register
    def _(self, obj: Form, indent: int = 0):
        current_indent = ' ' * (indent * 4)
        builtins = builtin_functions()

        if not obj.elements:
            return ""
        if not isinstance(obj.elements[0], Atom):
            raise SyntaxError(f"Expected Atom as first element of Form, but got {obj.elements[0]}")

        form_name = obj.elements[0].value
        if form_name in builtins:
            return f"{current_indent}{self.compile_builtin(obj)}"
        else:
            args = ','.join([self.compile_obj(element) for element in islice(obj.elements, 1, len(obj.elements))])
            return f"{current_indent}{form_name}({args})"


    def compile_builtin(self, form: Form):
        function_name = form.elements[0].value

        def create_body(delim: str, elements: islice | list = islice(form.elements, 1, len(form.elements))):
            return delim.join([self.compile_obj(element) for element in elements])

        def create_op(op: str, form: Form, n_args: int = 2):
            args = len(form.elements) - 1
            if args != n_args:
                raise TypeError(f"'{op}' takes {n_args} arguments but {args} were given!")
            return create_body(f' {op} ')

        match function_name:
            case "import":
                return f"import {form.elements[1].value}"
            case "print":
                return f"print({create_body(', ')})"
            case "+":
                return create_body(' + ')
            case "-":
                return create_body(' - ')
            case "*":
                return create_body(' * ')
            case "/":
                return create_body(' / ')
            case "not":
                n_args = len(form.elements) - 1
                if n_args != 1:
                    raise TypeError(f"'not' takes 1 argument but {n_args} were given!")
                return ' not ' + create_body('')
            case "and" | "or":
                return create_body(f' {function_name} ')
            case "<" | ">" | "<=" | ">=":
                return create_op(function_name, form)
            case "=":
                n_args = len(form.elements) - 1
                if n_args != 2:
                    raise TypeError(f"'=' takes 2 arguments but {n_args} were given!")
                return create_body(' == ')
            case "list":
                return f"list_create({create_body(', ')})"
            case "first":
                n_args = len(form.elements) - 1
                if n_args != 1:
                    raise TypeError(f"'first' takes 1 argument but {n_args} were given!")
                return f"{create_body('')}[0]"
            case "rest":
                n_args = len(form.elements) - 1
                if n_args != 1:
                    raise TypeError(f"'rest' takes 1 argument but {n_args} were given!")
                return f"{create_body('')}[1:]"
            case "++":
                return f"list_append({create_body(', ')})"
            case "map":
                n_args = len(form.elements) - 1
                if n_args != 2:
                    raise TypeError(f"'map' takes 2 arguments but {n_args} were given!")

                func = self.compile_obj(form.elements[1])
                collection = self.compile_obj(form.elements[2])
                return f"list(map({func}, {collection}))"
            case "filter":
                n_args = len(form.elements) - 1
                if n_args != 2:
                    raise TypeError(f"'filter' takes 2 arguments but {n_args} were given!")

                func = self.compile_obj(form.elements[1])
                collection = self.compile_obj(form.elements[2])
                return f"list(filter({func}, {collection}))"
            case "lambda":
                args = form.elements[1]
                if isinstance(args, Atom):
                    args = self.compile_obj(args)
                elif isinstance(args, Form):
                    args = create_body(', ', args.elements)
                else:
                    raise TypeError(f"Expected Form or Atom but got {type(args)}")
                return f"lambda {args}: {self.compile_obj(form.elements[2])}"
            case "if":
                n_args = len(form.elements) - 1
                if n_args != 3:
                    raise TypeError(f"if requires 3 arguments but {n_args} were given!")

                condition = self.compile_obj(form.elements[1])
                if_branch = self.compile_obj(form.elements[2])
                else_branch = self.compile_obj(form.elements[3])
                return f"({if_branch}) if ({condition}) else ({else_branch})"
        return ""


    def compile_function(self, function: Function, indent: int):
        builtins = builtin_functions()
        if function.name in builtins:
            logger.error(f"Error: builtin function {function.name} is being redefined.")

        def create_body(add_return: bool):
            return_f = lambda i: 'return ' if add_return and i == len(function.body) - 1 else ''
            total_indent = ' ' * (indent + 1) * 4
            body = [f"{total_indent}{return_f(i)}{self.compile_obj(obj, indent)}" for i, obj in enumerate(function.body)]
            return '\n'.join(body)


        if function.name == "main":
            output = f"if __name__ == '__main__':\n{create_body(False)}\n"
        else:
            output = f"def {function.name}({', '.join([arg.identifier for arg in function.args])}):\n{create_body(True)}"

        return output + "\n"


    def validate(self, objects) -> tuple[bool, str]:
        for obj in objects:
            if not isinstance(obj, Function) or not isinstance(obj, Form):
                return False, f"Got unexpected object at root-level: {obj}"
        return True, ""


    def compile_program(self, ast: AST, ext_funcs: dict[str, Function] = None, is_repl: bool = False) -> tuple[bool, str, dict]:
        if ext_funcs is None:
            ext_funcs = {}

        if not ast.children:
            return True, "", {}

        objects = [to_object(child) for child in ast.children]

        if not is_repl:
            validation_result, validation_message = self.validate(objects)
            if not validation_result:
                return False, validation_message, {}

        namespace = {
            **ext_funcs,
            **{obj.name: obj for obj in objects if isinstance(obj, Function)},
        }

        if not is_repl and 'main' not in namespace:
            return False, f"Function 'main' is not defined!", {}

        type_checker_result, namespace_types = check_types(namespace)
        if not type_checker_result:
            return False, namespace_types, ext_funcs

        output = self.convert_to_output(is_repl, namespace, namespace_types, objects)
        return True, output, namespace


    def convert_to_output(self, is_repl, namespace, namespace_types, objects):
        output = "from lisp_core import *\n\n"
        for function in namespace.values():
            output += self.compile_function(function, 0) + "\n"
        if is_repl:
            for function in objects:
                if not isinstance(function, Function):
                    result, inferred_type = infer_type(function, namespace_types)
                    if not result:
                        print(f"ERROR: {inferred_type}")
                        return ""
                    print(f"Inferred type: {inferred_type.name()}")
                    output += "\n" + self.compile_obj(function)
        return output
