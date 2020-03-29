import re
from typing import Callable, List, Iterable, cast, Deque
from nltk.tokenize import TweetTokenizer
from nltk.tokenize.treebank import TreebankWordDetokenizer
from .util import concat, split_include, iter_replace


ttk = TweetTokenizer()


url = re.compile(r'^https?://\S+$')
email = re.compile(r'^\S+@\S+$')
hsmiley = re.compile(r'([oOuU;T-])([wWg]|_+)([oOuU;T-])')
vsmiley = re.compile(r'[:;xX][-]?[oO()DPd]+')
number = r'^\d+$'
hexi = r'^0x[a-fA-F0-9]$'
time = r'^\d+:\d+$'
all_alphanum = re.compile(r'^[a-zA-Z0-9]+$')
one_nonalphanum = re.compile(r'[^a-zA-Z]')
initial_punct = re.compile(r'^[\'"*]')
terminal_punct = re.compile(r'[,.;:\'"?!*]$')
word_seps = re.compile(r'[\\(){}\[\]<>]')
post_url_word_seps = re.compile(r'[-]')


def string2words_helper2(word: str) -> Iterable[str]:
    # This splits a string, which is already cut to a word-boundary.
    # Usually, all non-alphanumerics will become its own token.
    # However, in some special cases (such as URLs and smileys), I will parse several non-alphanumerics in one token.
    # These tests should be ordered from most probable to least, except where the tests are non-disjoint.
    if all_alphanum.match(word) and not re.match(number, word):
        # This is the base case for regular words.
        # This is the common case, hence first.
        yield word.lower()
    elif not word:
        # skip empty string
        # before testing word[0]
        pass
    elif initial_punct.search(word[0]):
        yield word[0]
        yield from string2words_helper2(word[1:])
    elif terminal_punct.search(word[-1]):
        yield from string2words_helper2(word[:-1])
        yield word[-1]
    elif re.search(word_seps, word):
        for piece in split_include(word_seps, word):
            if len(piece) == 1 and re.match(word_seps, piece):
                yield piece
            else:
                yield from string2words_helper(piece)
    elif re.match(url, word):
        yield '<url>'
        yield word
    elif re.match(email, word):
        yield '<email>'
        yield word
    elif re.search(post_url_word_seps, word):
        for piece in split_include(post_url_word_seps, word):
            if len(piece) == 1 and re.match(post_url_word_seps, piece):
                yield piece
            else:
                yield from string2words_helper(piece)
    elif re.match(time, word):
        yield '<time>'
        yield word
    elif re.match(number, word):
        yield '<number>'
        yield word
    elif "'" in word[1:-1]:
        # Unfortunately, TweetTokenizer does not split on apostrophes
        # This is especially bad for posessive words, which in their
        # posessive form might only occur once.
        cut = word.find("'", 1)
        # word[:cut] and word[:cut] might not be simple alphanumeric
        yield word[:cut].lower()
        yield word[cut:].lower()
    # elif "/" in word[1:-1]:
    #     cut = word.find("/", 1)
    #     yield word[:cut].lower()
    #     yield word[cut:].lower()
    elif re.match(hexi, word):
        yield '<hexi>'
        yield word
    # elif re.match(hsmiley, word) or re.match(vsmiley, word) or word == r'¯\_(ツ)_/¯':
    #     yield word
    # elif re.match(r'\.{2,}', word):
    #     yield '<dots>'
    #     yield word
    elif word[0] == '@':
        yield '<at_tag>'
        yield word[1:]
    elif word[0] == '#':
        yield '<hash_tag>'
        yield word[1:]
    else:
        yield word.lower()


def string2words_helper(string: str) -> Iterable[str]:
    # for word in ttk.tokenize(string):

    # Level 1, tokenization: separate by whitespace.
    # I assume whitespace itself is never significant,
    # and its boundary is always significant.
    # There may be sub-boundaries I have yet to discover.
    for word in re.split(r'\s+', string):
        # one word here could be mulitple real words
        # string2words_helper2 cuts that up
        yield from string2words_helper2(word)
        # TODO: insert <nospace>

                    
def string2words(string: str) -> List[str]:
    return list(filter(bool, string2words_helper(string)))


def remove_ents(words: List[str]) -> Iterable[str]:
    skip = False
    for word in words:
        if skip:
            skip = False
            continue
        elif word.startswith('<') and word.endswith('>'):
            yield word
            skip = True
        else:
            yield word


tbwd = TreebankWordDetokenizer()
def words2string(words: Iterable[str]) -> str:
    s = cast(str, tbwd.detokenize(words))
    # put contractions back together
    s = re.sub(r' (\'[a-v])', r'\1', s)
    return s
