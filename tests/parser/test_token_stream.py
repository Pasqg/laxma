from parser.token_stream import TokenStream

def test_bool():
    empty_stream = TokenStream([])
    stream = TokenStream([1, 2, 3])

    assert not empty_stream
    assert stream

def test_stream():
    stream = TokenStream([1, 2, 3])

    assert stream.advance() == (1, TokenStream([1, 2, 3], 1))
    assert stream.advance()[1].advance() == (2, TokenStream([1, 2, 3], 2))
    assert stream.advance()[1].advance()[1].advance() == (3, TokenStream([1, 2, 3], 3))

