import random
from typing import Counter, DefaultDict, List, Dict, Tuple, Iterable, Any, cast
from nltk.util import ngrams
from tqdm import tqdm
import numpy as np
from .util import Exchange, concat, merge_dicts, bar, interactive_loop, reverse, imap
from .string2words import string2words, remove_ents, words2string


def exchange2words(prompt_response: Tuple[str, str]) -> Tuple[List[str], List[str]]:
    return (string2words(prompt_response[0]), string2words(prompt_response[1]))


def exchanges_stats(
        exchanges_: Iterable[Exchange], interactive: bool = False
) -> List[Exchange]:
    print(bar)
    exchanges = list(exchanges_)
    print(f'Number of exchanges: {len(exchanges)}')
    exchanged_words = list(map(exchange2words, exchanges))

    print(bar)

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
            print(f'{count: 3d} {words2string(gram)}')

    print(bar)
    ents: DefaultDict[str, Counter[str]] = DefaultDict(Counter)
    for msg_pair in exchanged_words:
        for msg in msg_pair:
            for word, next_word in zip(msg[:-1], msg[1:]):
                if word.startswith('<') and word.endswith('>'):
                    ents[word][next_word] += 1
    for ent_name, counter in ents.items():
        print(f'Top {ent_name}:', end=' ')
        for ent_val, count in counter.most_common(10):
            print(ent_val, end=' ')
        print()

    print(bar)

    print('Rare and valuable words (least common):')
    for _word, count in reverse(n_gram_counters[1].most_common())[:150]:
        if count > 1:
            break
        word = _word[0]
        print(count, word)

    print(bar)
    print('Randomly selected chats')
    print()

    rnge = cast(Iterable[Any], interactive_loop() if interactive else range(100))

    for _ in rnge:
        prompt, response = random.choice(exchanges)
        print(f'them: {prompt}')
        print(f'{string2words(prompt)}')
        print(f'you: {response}')
        print(f'{string2words(response)}')
        print()

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
