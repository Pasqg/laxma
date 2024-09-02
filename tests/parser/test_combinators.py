from parser.ast import AST
from parser.combinators import or_match, and_match, at_least_one, match_none, match_any
from parser.string_combinators import match_str, lit
from parser.token_stream import TokenStream


def test_match_none():
    tokens = TokenStream(["func"])

    parser = match_none("NONE")

    assert parser(tokens) == (True, AST("NONE"), tokens)


def test_match_any():
    tokens = TokenStream(["func"])

    parser = match_any()

    assert parser(tokens) == (True, AST(None, ["func"], []), TokenStream(["func"], 1))


def test_match_any_but_excluded():
    tokens = TokenStream(["func"])

    parser = match_any(excluded=lit("func"))

    assert parser(tokens) == (False, AST(), TokenStream(["func"], 0))


def test_or():
    tokens_func = TokenStream(["func"])
    tokens_fanc = TokenStream(["fanc"])
    tokens_fenc = TokenStream(["fenc"])

    parser = or_match("OR", match_str("FUNC", "func"), match_str("FANC", "fanc"))

    assert parser(tokens_func) == (True, AST("OR", ["func"], [AST("FUNC", ["func"])]), tokens_func.advance()[1])
    assert parser(tokens_fanc) == (True, AST("OR", ["fanc"], [AST("FANC", ["fanc"])]), tokens_fanc.advance()[1])
    assert parser(tokens_fenc) == (False, AST(), tokens_fenc)


def test_and():
    tokens_func_fanc = TokenStream(["func", "fanc"])
    tokens_func_fenc = TokenStream(["func", "fenc"])

    parser = and_match("AND", match_str("FUNC", "func"), match_str("FANC", "fanc"))

    assert parser(tokens_func_fanc) == (True,
                                        AST("AND", ["func", "fanc"], [AST("FUNC", ["func"]), AST("FANC", ["fanc"])]),
                                        tokens_func_fanc.advance()[1].advance()[1])
    assert parser(tokens_func_fenc) == (False, AST(), tokens_func_fenc)


def test_list_one_element():
    parser = at_least_one("LIST", element=match_str("FUNC", "func"))

    tokens_func = TokenStream(["func"])
    func_ast = AST("FUNC", ["func"])
    assert parser(tokens_func) == (True,
                                   AST("LIST", ["func"], [func_ast]),
                                   tokens_func.advance()[1])


def test_list_two_elements():
    parser = at_least_one("LIST", element=match_str("FUNC", "func"))
    tokens_func_func = TokenStream(["func", "func"])
    func_ast = AST("FUNC", ["func"])
    assert parser(tokens_func_func) == (True,
                                        AST("LIST", ["func", "func"],
                                            [func_ast, func_ast]),
                                        tokens_func_func.advance()[1].advance()[1])


def test_list_three_elements():
    parser = at_least_one("LIST", element=match_str("FUNC", "func"))
    tokens_func_func_func = TokenStream(["func", "func", "func", "fanc"])
    func_ast = AST("FUNC", ["func"])
    assert parser(tokens_func_func_func) == (True,
                                             AST("LIST", ["func", "func", "func"],
                                                 [func_ast, func_ast, func_ast]),
                                             tokens_func_func_func.advance()[1].advance()[1].advance()[1])


def test_list_no_delim():
    parser = at_least_one("LIST", element=match_str("FUNC", "func"), delim=match_str("+", "+"))

    tokens_func = TokenStream(["func"])
    func_ast = AST("FUNC", ["func"])
    assert parser(tokens_func) == (True,
                                   AST("LIST", ["func"], [func_ast]),
                                   tokens_func.advance()[1])


def test_list_one_delim():
    parser = at_least_one("LIST", element=match_str("FUNC", "func"), delim=match_str("+", "+"))

    tokens_func = TokenStream(["func", "+", "func", "+"])
    func_ast = AST("FUNC", ["func"])
    plus_ast = AST("+", ["+"])
    assert parser(tokens_func) == (True,
                                   AST("LIST", ["func", "+", "func"],
                                       [func_ast, plus_ast, func_ast]),
                                   tokens_func.advance()[1].advance()[1].advance()[1])


def test_list_two_delim():
    parser = at_least_one("LIST", element=match_str("FUNC", "func"), delim=match_str("+", "+"))

    tokens_func = TokenStream(["func", "+", "func", "+", "func", "+"])
    func_ast = AST("FUNC", ["func"])
    plus_ast = AST("+", ["+"])
    assert parser(tokens_func) == (True,
                                   AST("LIST", ["func", "+", "func", "+", "func"],
                                       [func_ast, plus_ast, func_ast, plus_ast, func_ast]),
                                   tokens_func.advance()[1].advance()[1].advance()[1].advance()[1].advance()[1])


def test_list_no_match():
    parser = at_least_one("LIST", element=match_str("FUNC", "func"), delim=match_str("+", "+"))

    tokens_func = TokenStream(["fanc"])
    assert parser(tokens_func) == (False, AST(), tokens_func)
