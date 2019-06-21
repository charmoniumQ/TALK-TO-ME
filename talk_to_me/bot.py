from typing import Iterable, Tuple, List
from seq2seq.models import Seq2Seq
from tqdm import tqdm
from .words2vectors import Words2Vectors
from .util import transpose, Exchange


class Bot:
    def __init__(self) -> None:
        self.vectors2vectors = Seq2Seq(
            batch_input_shape=(16, 7, 5), hidden_dim=10,
            output_length=8, output_dim=20, depth=2, peek=True,
        )
        self.vectors2vectors.compile(loss='mse', optimizer='rmsprop')
        self.words2vectors = Words2Vectors()

    def fit(self, exchanges: Iterable[Exchange]) -> None:
        sentences = list(map(list, set(
            tuple(message) for exchange in exchanges for message in exchange
        )))
        self.words2vectors.fit(sentences)
        prompts, responses = transpose(exchanges)
        self.vectors2vectors.fit(
            [self.words2vectors.transform(prompt) for prompt in prompts],
            [self.words2vectors.transform(response) for response in responses],
        )

    def transform(self, prompt: List[str]) -> List[str]:
        prompt_vector = self.words2vectors.transform(prompt)
        response_vector = self.vectors2vectors.transform(prompt_vector)
        return self.words2vectors.inverse_transform(response_vector)
