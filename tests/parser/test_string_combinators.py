from parser.ast import AST
from parser.string_combinators import match_str, match_regex
from parser.token_stream import TokenStream


def test_str():
    parser = match_str("FOR-LOOP", "for")

    assert parser(TokenStream(["for"])) == (True, AST("FOR-LOOP", ["for"], None), TokenStream(["for"]).advance()[1])
    assert parser(TokenStream(["for", "a"])) == (True, AST("FOR-LOOP", ["for"], None), TokenStream(["for", "a"]).advance()[1])
    assert parser(TokenStream(["for2"])) == (False, AST(), TokenStream(["for2"]))


def test_regex():
    parser = match_regex("FOR-LOOP", "for$")

    assert parser(TokenStream(["for"])) == (True, AST("FOR-LOOP", ["for"], None), TokenStream(["for"]).advance()[1])
    assert parser(TokenStream(["for2"])) == (False, AST(), TokenStream(["for2"]))
