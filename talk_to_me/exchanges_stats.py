import random
from typing import Counter
from typing import List, Dict, Tuple, Iterable
from nltk.util import ngrams
import numpy as np
from .util import Exchange, concat, merge_dicts
# from .words2sentence import words2sentence


bar = '\u2500' * 80


def exchanges_stats(exchanges: List[Exchange]) -> None:
    print(bar)
    print(f'Number of exchanges: {len(exchanges)}')
    print(f'Average prompt words: {np.mean([len(prompt) for prompt, _ in exchanges])}')
    print(f'Average response words: {np.mean([len(response) for _, response in exchanges])}')

    def gen_sentences() -> Iterable[List[str]]:
        def remove_ent(sentence: List[str]) -> Iterable[str]:
            skip = False
            for word in sentence:
                if skip:
                    skip = False
                    continue
                elif word.startswith('<') and word.endswith('>'):
                    yield word
                    skip = True
                else:
                    yield word
        for prompt, response in exchanges:
            yield list(remove_ent(prompt))
            yield list(remove_ent(response))

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
        # print('Ctrl+D to exit')
        print()
        # while True:
        for _ in range(100):
            prompt, response = random.choice(exchanges)
            print(f'them: {prompt}')
            print(f'you: {response}')
            print()
            # input()
    except EOFError:
        pass


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
