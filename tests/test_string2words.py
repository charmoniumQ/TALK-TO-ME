from talk_to_me.string2words import string2words, words2string

def test_string2words_contraction():
    assert string2words('I\'ve') \
        == ['i', '\'ve']

def test_string2words_punct_single():
    assert string2words('*Hello, where are you!? Cool.') \
        == ['*', 'hello', ',', 'where', 'are', 'you', '!', '?', 'cool', '.']

def test_string2words_embedded_punct():
    assert string2words('sam\'s \'a.b.c\' abc-def') \
        == ['sam', '\'s', '\'', 'a.b.c', '\'', 'abc', '-', 'def']

def test_string2words_numbers():
    assert string2words('8:30 7-1 9.1.2') \
        == ['<time>', '8:30', '<number>', '7', '-', '<number>', '1', '9.1.2']

def test_string2words_brackets():
    assert string2words('a(bc) d[ef] h{ij} k<lm> n-o-p') \
        == ['a', '(', 'bc', ')', 'd', '[', 'ef', ']', 'h', '{', 'ij', '}',
            'k', '<', 'lm', '>', 'n', '-', 'o', '-', 'p']

def test_string2words_escape():
    assert string2words('<abc></abc>') \
        == ['<', 'abc', '>', '<', '/abc', '>']

# # TODO: this
# def test_string2words_path():
#     assert string2words('/abc/def') \
#         == ['/abc', '/def']
