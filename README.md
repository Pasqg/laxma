# Laxma

This project provides simple parser combinators in python. Tokens can have any type.

# Description

A parser is a function that takes a TokenStream as input and outputs a ParseResult. The ParseResult contains:

- A boolean that indicates whether parsing was successful.
- An AST (Abstract Syntax Tree) that represents the token stream.
- The remaining tokens in the stream.

One can build a fully fledged parser in one "block", but that would be fairly complex and very hard to get right and
maintain. Instead, parsers can be built up in a modular way from smaller parsers using utilities called parsers
combinators.

## Parser combinators

A parser combinator is a higher-order function that takes an optional name/id to identify a grammar rule (useful for
searching in the tree during the compilation stage) and a list of combinators. It outputs a parser function.

Simple parsers, matching a single token either literally or through patterns/regex, can be used as building blocks when
combined as logical 'ORs' and 'ANDs' or in collection such as 'LISTs'.

A variable assignment is usually composed by an identifier, an equal sign (or equivalent operator) and a value (a
literal or an expression). The natural language description of this parser should already give away the implementation
through a parser combinator:

`variable_assignment = and_match(identifier, lit("="), expression)`

The 'and_match' combinator will succeed if all its input (composed) parsers succeed, otherwise it will fail. It is very
easy to change and extend grammars in the future: if our `identifier` becomes more complex (accessing members,
destructuring), we can just concentrate on updating `identifier` parser.

Similarly, a `or_match` combinator will succeed when any of its input parsers succeeds (the first to succeed). It fails
when no parser matches the remaining tokens.

Note: the OR combinator implicitly performs backtracking. Care must be taken with the amount of backtracking a grammar
will end up doing, as this will really affect performance.

## Available combinators

- `lit(s: str)`: matches a string token literally.
- `regex(s: str)`: matches a string token.
- `match_none()`: always returns True and matches nothing.
- `match_any(excluded)`: always matches the next token if it doesn't match excluded.
- `or_match(id, *parsers)`: tries each input parser in order until one matches, otherwise it will fail.
- `and_match(id, *parsers)`: tries to match all the input parsers in sequence (on the remaining tokens not parsed by
  previous parser) and fails if it can't match all of them.
- `many(id, element, delim)`: matches sequences like `element + optional[delim] + element + ... + optional[delim] +
  element`. Allows zero matches.
- `at_least_one(id, element, delim)`: like `many` but requires at least a match of `element` parser.
- `discard(parser)`: discards the AST created by parser (while retaining its success/failure and advanced token stream).
  Useful to prune unnecessary nodes for later stages.
- `ref(lambda tokens: parser(tokens))`: creates a reference to `parser` which might not have been defined yet. Useful to
  create self/mutually recursive parsers.

## Examples

See [examples/lisp](examples/lisp)

The grammar of a simple dialect of lisp can be described as:

``` python
number = regex(r"\d+|\d+\.\d+")
string = regex(r'"[^"]*"')
identifier = regex(r"[a-zA-Z\-\+0-9]+")
atom = or_match(LispRule.ATOM, identifier, number, string)

element = or_match(LispRule.ELEMENT, ref(lambda t: form(t)), atom)
form = and_match(LispRule.FORM, lit("("), many(LispRule.ELEMENTS, element=element), lit(")"))

program = at_least_one(LispRule.PROGRAM, element=form)
```

This grammar can parse text such as:

```lisp
(fun add (x y) (+ x y))

(fun main () (print (add 2 3)))
```

The pruned AST produced by the parser:

```
+- LispRule.PROGRAM: ( fun add ( x y ) ( + x y ) ) ( fun main ( ) ( print ( add 2 3 ) ) )
|  +- LispRule.FORM: ( fun add ( x y ) ( + x y ) )
|  |  +- LispRule.ELEMENTS: fun add ( x y ) ( + x y )
|  |  |  +- LispRule.ATOM: fun
|  |  |  +- LispRule.ATOM: add
|  |  |  +- LispRule.FORM: ( x y )
|  |  |  |  +- LispRule.ELEMENTS: x y
|  |  |  |  |  +- LispRule.ATOM: x
|  |  |  |  |  +- LispRule.ATOM: y
|  |  |  +- LispRule.FORM: ( + x y )
|  |  |  |  +- LispRule.ELEMENTS: + x y
|  |  |  |  |  +- LispRule.ATOM: +
|  |  |  |  |  +- LispRule.ATOM: x
|  |  |  |  |  +- LispRule.ATOM: y
|  +- LispRule.FORM: ( fun main ( ) ( print ( add 2 3 ) ) )
|  |  +- LispRule.ELEMENTS: fun main ( ) ( print ( add 2 3 ) )
|  |  |  +- LispRule.ATOM: fun
|  |  |  +- LispRule.ATOM: main
|  |  |  +- LispRule.FORM: ( )
|  |  |  |  +- LispRule.ELEMENTS: 
|  |  |  +- LispRule.FORM: ( print ( add 2 3 ) )
|  |  |  |  +- LispRule.ELEMENTS: print ( add 2 3 )
|  |  |  |  |  +- LispRule.ATOM: print
|  |  |  |  |  +- LispRule.FORM: ( add 2 3 )
|  |  |  |  |  |  +- LispRule.ELEMENTS: add 2 3
|  |  |  |  |  |  |  +- LispRule.ATOM: add
|  |  |  |  |  |  |  +- LispRule.ATOM: 2
|  |  |  |  |  |  |  +- LispRule.ATOM: 3
```

# Error reporting

 ### 🚧 Work in progress 🚧

# License

This project is licensed under [Apache 2.0 license](LICENSE).