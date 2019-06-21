import re
from typing import Callable, List, Iterable
from nltk.tokenize import TweetTokenizer
from .util import concat, split_include


_sent2words = TweetTokenizer()


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
        elif re.match(r'([oOuU;T-])([wWg]|_+)\1', word):
            yield '<hsmiley>'
            yield word
        elif re.match(r'[:;xX][-]?[oO()DPd]+', word):
            yield '<vsmiley>'
            yield word
        elif re.match(r"\S+'\S+", word):
            cut = word.find("'")
            yield word[:cut]
            yield word[cut:]
        else:
            new_words = filter(bool, split_include("'|-|:|/", word))
            for new_word in new_words:
                if re.match(r'^\d+$', new_word):
                    yield '<number>'
                    yield new_word
                else:
                    yield new_word.lower()

    return list(concat([retokenize(word) for word in words]))
