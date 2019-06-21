from typing import Iterable, Tuple, List, Dict, Any
from gensim.models import FastText
from tqdm import tqdm
from .util import n_procs, nparray


class Words2Vectors:
    def __init__(self) -> None:
        self.encoder = FastText(size=100, window=5, min_count=5, workers=n_procs, sg=1)

    def fit(self, sentences: List[List[str]]) -> None:
        self.encoder.build_vocab(sentences=sentences)
        sentences = tqdm(sentences, desc='train w2v', total=len(sentences))
        self.encoder.train(sentences=sentences, total_examples=len(sentences), epochs=10)

    def transform(self, words: List[str]) -> List[nparray]:
        return [self.encoder.wv[word] for word in words]

    def inverse_transform(self, vectors: List[nparray]) -> List[str]:
        return [self.encoder.closest(vector) for vector in vectors]
