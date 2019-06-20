import random
from typing import List
from .util import Exchange
# from .words2sentence import words2sentence


def exchanges_stats(exchanges: List[Exchange]) -> None:
    print(f'len: {len(exchanges)}')
    try:
        print('Ctrl+D to exit')
        while True:
            prompt, response = random.choice(exchanges)
            print(f'them: {prompt}')
            print(f'you: {response}')
            input()
    except EOFError:
        pass
