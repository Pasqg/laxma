from parser.ast import AST
from parser.combinators import orMatch, andMatch, listParser, matchNone
from parser.string_combinators import matchStr
from parser.token_stream import TokenStream


def test_match_none():
    tokens = TokenStream(["func"])

    parser = matchNone("NONE")

    assert parser(tokens) == (True, AST("NONE"), tokens)


def test_or():
    tokens_func = TokenStream(["func"])
    tokens_fanc = TokenStream(["fanc"])
    tokens_fenc = TokenStream(["fenc"])

    parser = orMatch("OR", matchStr("FUNC", "func"), matchStr("FANC", "fanc"))

    assert parser(tokens_func) == (True, AST("OR", ["func"], [AST("FUNC", ["func"])]), tokens_func.advance()[1])
    assert parser(tokens_fanc) == (True, AST("OR", ["fanc"], [AST("FANC", ["fanc"])]), tokens_fanc.advance()[1])
    assert parser(tokens_fenc) == (False, AST(), tokens_fenc)


def test_and():
    tokens_func_fanc = TokenStream(["func", "fanc"])
    tokens_func_fenc = TokenStream(["func", "fenc"])

    parser = andMatch("AND", matchStr("FUNC", "func"), matchStr("FANC", "fanc"))

    assert parser(tokens_func_fanc) == (True,
                                        AST("AND", ["func", "fanc"], [AST("FUNC", ["func"]), AST("FANC", ["fanc"])]),
                                        tokens_func_fanc.advance()[1].advance()[1])
    assert parser(tokens_func_fenc) == (False, AST(), tokens_func_fenc)


def test_list_one_element():
    parser = listParser("LIST", element=matchStr("FUNC", "func"))

    tokens_func = TokenStream(["func"])
    func_ast = AST("FUNC", ["func"])
    assert parser(tokens_func) == (True,
                                   AST("LIST", ["func"], [func_ast]),
                                   tokens_func.advance()[1])


def test_list_two_elements():
    parser = listParser("LIST", element=matchStr("FUNC", "func"))
    tokens_func_func = TokenStream(["func", "func"])
    func_ast = AST("FUNC", ["func"])
    assert parser(tokens_func_func) == (True,
                                        AST("LIST", ["func", "func"],
                                            [func_ast, AST("LIST", ["func"], [func_ast])]),
                                        tokens_func_func.advance()[1].advance()[1])


def test_list_three_elements():
    parser = listParser("LIST", element=matchStr("FUNC", "func"))
    tokens_func_func_func = TokenStream(["func", "func", "func", "fanc"])
    func_ast = AST("FUNC", ["func"])
    assert parser(tokens_func_func_func) == (True,
                                             AST("LIST", ["func", "func", "func"],
                                                 [func_ast, AST("LIST", ["func", "func"],
                                                                [func_ast, AST("LIST", ["func"], [func_ast])])]),
                                             tokens_func_func_func.advance()[1].advance()[1].advance()[1])


def test_list_no_delim():
    parser = listParser("LIST", element=matchStr("FUNC", "func"), delim=matchStr("+", "+"))

    tokens_func = TokenStream(["func"])
    func_ast = AST("FUNC", ["func"])
    assert parser(tokens_func) == (True,
                                   AST("LIST", ["func"], [func_ast]),
                                   tokens_func.advance()[1])


def test_list_one_delim():
    parser = listParser("LIST", element=matchStr("FUNC", "func"), delim=matchStr("+", "+"))

    tokens_func = TokenStream(["func", "+", "func", "+"])
    func_ast = AST("FUNC", ["func"])
    plus_ast = AST("+", ["+"])
    assert parser(tokens_func) == (True,
                                   AST("LIST", ["func", "+", "func"],
                                       [func_ast, plus_ast, AST("LIST", ["func"], [func_ast])]),
                                   tokens_func.advance()[1].advance()[1].advance()[1])


def test_list_no_match():
    parser = listParser("LIST", element=matchStr("FUNC", "func"), delim=matchStr("+", "+"))

    tokens_func = TokenStream(["fanc"])
    assert parser(tokens_func) == (False, AST(), tokens_func)
