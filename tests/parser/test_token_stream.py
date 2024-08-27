from parser.token_stream import TokenStream


def test_empty():
    empty_stream = TokenStream([])
    stream = TokenStream([1, 2, 3])

    assert not empty_stream
    assert stream
