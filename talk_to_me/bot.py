from typing import Iterable, Tuple, List, cast
# from seq2seq.models import Seq2Seq
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Masking, Embedding
from keras.callbacks import EarlyStopping, ModelCheckpoint
from gensim.models import FastText
import numpy as np
from .string2words import string2words, remove_ents
from .words2string import words2string
from .util import transpose, Exchange, bar, n_procs, concat, invert, nparray


# TODO: encoding layer as part of NN
# TODO: character-to-character learning
# TODO: learn rare words as UNK isntead
# TODO: train an entity-generator.

class Word2Int:
    def fit(self, words: Iterable[str]) -> None:
        # remove <end>, bring it to the front
        # add in <unk>
        all_words = sorted(list(set(words) | {'<unk>'}))

        self.int2word = dict(enumerate(all_words))
        self.word2int = invert(self.int2word)

    def transform(self, word: str) -> int:
        return self.word2int.get(word, self.word2int['<unk>'])

    def inverse_transform(self, word: int) -> str:
        return self.int2word.get(word, '<unk>')

    def __len__(self) -> int:
        return len(self.int2word)

class Int2Vec:
    def __init__(self, n: int):
        self.n = n

    def transform(self, idx: int) -> nparray:
        vec = np.zeros(self.n, dtype=int)
        vec[idx] = 1
        return vec

    def inverse_transform(self, vec: nparray) -> int:
        return cast(int, vec.argmax())

class Bot:
    def __init__(self) -> None:
        self.encoding_size = 100
        self.encoding_window = 7

        self.word2int = Word2Int()
        # self.word2vector = FastText(
        #     size=self.encoding_size, window=5, min_count=2, workers=n_procs,
        # )
        # self.vectors2vectors = Seq2Seq(
        #     batch_input_shape=(16, 7, 5), hidden_dim=10,
        #     output_length=8, output_dim=20, depth=2, peek=True,
        # )

    def fit(self, exchanges: List[Exchange]) -> None:
        exchanged_words = [
            (
                list(remove_ents(string2words(prompt))),
                list(remove_ents(string2words(response))),
            )
            for prompt, response in exchanges
        ]

        # I use `lambda message: list(message)` instead of `list` to satisfy mypy
        words = [
            word
            for exchange in exchanged_words
            for message in exchange
            for word in message
        ]

        self.word2int.fit(words)
        self.int2vec = Int2Vec(len(self.word2int))


        # many-to-one RNN
        # w_0 w_1 ... [w_i w_{i+1} ... w_{i+w}]
        #             | |
        #             | |
        #             | |
        #              V
        # v_0 v_1 ... v_i
        self.vectors2vectors = Sequential([
            Embedding(
                input_dim=len(self.word2int),
                input_length=self.encoding_window,
                output_dim=100,
                mask_zero=True,
            ),
            Dense(64, activation='relu'),
            LSTM(
                64, return_sequences=False, 
                dropout=0.1, recurrent_dropout=0.1,
            ),
            Dropout(0.5),
            Dense(len(self.word2int), activation='softmax'),
        ])
        self.vectors2vectors.compile(
            optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy']
        )

        # self.word2vector.build_vocab(sentences=messages)
        # self.word2vector.train(
        #     sentences=messages, total_examples=len(messages), epoch=10,
        # )

        xs = []
        ys = []
        for exchange in exchanged_words:
            prompt, response = exchange
            padding_length = len(prompt) - len(response) + self.encoding_window
            if padding_length > 0:
                prompt = prompt + ['<empty>'] * padding_length
            for i in range(len(response)):
                xs.append([
                    self.int2vec.transform(self.word2int.transform(word))
                    for word in prompt[i:i + self.encoding_window]
                ])
                ys.append(self.int2vec.transform(self.word2int.transform(response[i])))

        npxs, npys = np.array(xs), np.array(ys)

        self.vectors2vectors.fit(
            npxs, npys,
            batch_size=2048, epochs=150,
            callbacks=[
                EarlyStopping(monitor='val_loss', patience=5),
                ModelCheckpoint(
                    'model.h5',
                    save_best_only=True,
                    save_weights_only=False,
                ),
            ],
        )

    def transform(self, prompt_string: str) -> str:
        prompt_words = list(map(
            self.int2vec.transform,
            map(
                self.word2int.transform,
                string2words(prompt_string)
            )
        ))
        response_words = self.vectors2vectors.transform(prompt_words)
        response_string = words2string(
            list(map(self.word2int.inverse_transform,
                     map(self.int2vec.inverse_transform, response_words)
            ))
        )
        return response_string

    def interact(self) -> None:
        try:
            print('Ctrl+D to exit')
            while True:
                prompt = ''
                while not prompt:
                    prompt = input('> ')
                print(self.transform(prompt))
        except EOFError:
            pass
