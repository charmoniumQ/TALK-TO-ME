import random
import itertools
from typing import Counter, List, Dict, Tuple, Iterable
from nltk.util import ngrams
from tqdm import tqdm
import numpy as np
from .util import Exchange, concat, merge_dicts, bar
from .string2words import string2words, remove_ents


def exchanges_stats(
        exchanges_: Iterable[Exchange], interactive: bool = False
) -> List[Exchange]:
    print(bar)
    exchanges = list(tqdm(exchanges_, desc='loading data'))
    print(f'Number of exchanges: {len(exchanges)}')
    exchanged_words = [
        (string2words(prompt), string2words(response))
        for prompt, response in exchanges
    ]
    avg_prompt = np.mean([len(prompt) for prompt, _ in exchanged_words])
    print(f'Average prompt words: {avg_prompt:.1f}')
    avg_response = np.mean([len(response) for _, response in exchanged_words])
    print(f'Average response words: {avg_response:.1f}')

    def gen_sentences() -> Iterable[List[str]]:
        for prompt, response in exchanged_words:
            yield list(remove_ents(prompt))
            yield list(remove_ents(response))

    n_gram_counters = get_n_grams(list(gen_sentences()), max_n=5)
    for n, n_gram_counter in sorted(n_gram_counters.items()):
        num_of_grams = {0: 1, 1: 50, 2: 30, 3: 30, 4: 30, 5: 30}[n]
        print(bar)
        print(f'Most common {n}-grams:')
        for gram, count in n_gram_counter.most_common(num_of_grams):
            print(f'{count: 3d} {" ".join(gram)}')

    try:
        print(bar)
        print('View some of your hand-picked cringiest moments, courtesy of RNG')
        print()

        rnge: Iterable[int] = itertools.count() if interactive else range(100)

        if interactive:
            print('Ctrl+D to exit')

        for _ in rnge:
            prompt, response = random.choice(exchanges)
            print(f'them: {prompt}')
            print(f'you: {response}')
            print()
            # input()
    except EOFError:
        pass

    return exchanges


def get_n_grams(
        sentences: List[List[str]], max_n: int = 3
) -> Dict[int, Counter[Tuple[str, ...]]]:
    return merge_dicts([
        {
            n: Counter(concat([
                ngrams(sentence, n)
                for sentence in sentences
            ]))
            for n in range(1, max_n + 1)
        },
        {
            0: Counter({
                (): sum(map(len, sentences))
            }),
        },
    ])
