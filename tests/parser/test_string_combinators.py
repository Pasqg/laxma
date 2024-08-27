from parser.ast import AST
from parser.string_combinators import matchStr, matchRegex
from parser.token_stream import TokenStream


def test_str():
    parser = matchStr("FOR-LOOP", "for")

    assert parser(TokenStream(["for"])) == (True, AST("FOR-LOOP", ["for"], None), TokenStream(["for"]).advance()[1])
    assert parser(TokenStream(["for", "a"])) == (True, AST("FOR-LOOP", ["for"], None), TokenStream(["for", "a"]).advance()[1])
    assert parser(TokenStream(["for2"])) == (False, AST(), TokenStream(["for2"]))


def test_regex():
    parser = matchRegex("FOR-LOOP", "for$")

    assert parser(TokenStream(["for"])) == (True, AST("FOR-LOOP", ["for"], None), TokenStream(["for"]).advance()[1])
    assert parser(TokenStream(["for2"])) == (False, AST(), TokenStream(["for2"]))
