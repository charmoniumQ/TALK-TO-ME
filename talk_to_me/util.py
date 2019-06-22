import itertools
import multiprocessing
import re
import os
import functools
from typing import TypeVar, Callable, Iterable, List, cast, Any, Tuple, Dict


_X = TypeVar('_X')
def concat(it: Iterable[Iterable[_X]]) -> Iterable[_X]:
    return itertools.chain.from_iterable(it)


n_procs = os.cpu_count() or 1
_pool = multiprocessing.Pool(n_procs)
_T = TypeVar('_T')
_U = TypeVar('_U')
def imap(func: Callable[[_T], _U], iterable: List[_T]) -> Iterable[_U]:
    chunk_size = len(iterable) // n_procs // 20
    return _pool.imap_unordered(func, iterable, chunk_size)


#_V = TypeVar('_V')
_V = Any
# _IterableF = TypeVar('_IterableF', bound=)
# _ListF = TypeVar('_ListF', bound=)
def list_f(func: Callable[..., Iterable[_V]]) -> Callable[..., List[_V]]:
    @functools.wraps(func)
    def func2(*args: Any, **kwargs: Any) -> List[_V]:
        return list(func(*args, **kwargs))
    return cast(Callable[..., List[_V]], func2)


Exchange = Tuple[List[str], List[str]]


_W = TypeVar('_W')
def transpose(lists: Iterable[Iterable[_W]]) -> Iterable[Iterable[_W]]:
    return list(zip(*lists))


nparray = Any


def split_include(delim_re: str, string: str) -> Iterable[str]:
    def get_breakpoints() -> Iterable[int]:
        yield 0
        for match in re.finditer(delim_re, string):
            yield match.start()
            yield match.end()
        yield len(string)

    breakpoints = list(get_breakpoints())
    for start, end in zip(breakpoints[:-1], breakpoints[1:]):
        yield string[start:end]


_Key = TypeVar('_Key')
_Val = TypeVar('_Val')
def merge_dicts(dcts: Iterable[Dict[_Key, _Val]]) -> Dict[_Key, _Val]:
    big_dct: Dict[_Key, _Val] = {}
    for dct in dcts:
        big_dct.update(dct)
    return big_dct


bar = '\u2500' * 80
