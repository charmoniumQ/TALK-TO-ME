import re
from typing import Callable, List, Iterable
from nltk.tokenize import TweetTokenizer
from .util import concat, split_include


_sent2words = TweetTokenizer()
sent2words: Callable[[str], List[str]] = _sent2words.tokenize


def sent2words(sent: str) -> List[str]:
    words = _sent2words.tokenize(sent)

    def retokenize(word: str) -> Iterable[str]:
        # TODO: retokenize ascii smileys as one token
        if re.match(r'^https?://\S+$', word):
            yield '<url>'
            yield word
        elif re.match(r'^\S+@\S+$', word):
            yield '<email>'
            yield word
        elif re.match(r'([oOuU-])([wWg]|_+)\1', word):
            yield '<hsmiley>'
            yield word
        elif re.match(r'[:;xX][-]?[()DPd]+', word):
            yield '<vsmiley>'
            yield word
        else:
            new_words = filter(bool, split_include("'|-|:|/", word))
            for new_word in new_words:
                if re.match(r'^\d+$', new_word):
                    yield '<number>'
                    yield new_word
                else:
                    yield new_word.lower()
    return list(concat([retokenize(word) for word in words]))
