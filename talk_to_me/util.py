import itertools
import multiprocessing
import re
import os
import functools
from typing import (
    TypeVar, Callable, Iterable, List, cast, Any, Tuple, Dict,
    Generator, Collection, Sized, Iterator, Optional, TYPE_CHECKING,
    Pattern, Union,
)


# iterables.chain.from_iterable is a long and ugly name
concat = itertools.chain.from_iterable


n_procs = os.cpu_count() or 1
_T = TypeVar('_T')
_U = TypeVar('_U')
if TYPE_CHECKING:
    pool_type = multiprocessing.pool.Pool
else:
    pool_type = None
_pool: Optional[pool_type] = None
def imap(func: Callable[[_T], _U], iterable: Collection[_T]) -> Iterable[_U]:
    global _pool
    if not _pool:
        _pool = multiprocessing.Pool(n_procs)
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


Exchange = Tuple[str, str]


_W = TypeVar('_W')
def transpose(lists: Iterable[Iterable[_W]]) -> Iterable[Iterable[_W]]:
    return list(zip(*lists))


nparray = Any


def split_include(delim_re: Union[str, Pattern[str]], string: str) -> Iterable[str]:
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

_Key2 = TypeVar('_Key2')
_Val2 = TypeVar('_Val2')
def invert(dct: Dict[_Key2, _Val2]) -> Dict[_Val2, _Key2]:
    return {val: key for key, val in dct.items()}


def interactive_loop() -> Generator[str, None, List[str]]:
    print('Press Enter to submit, Ctrl+D to quit')
    inputs = []
    try:
        while True:
            inputs.append(input())
            yield inputs[-1]
    except EOFError:
        pass
    return inputs


def _intercalate_helper(lst: Iterator[_T], sep: _T) -> Iterator[_T]:
    for elem in lst:
        yield sep
        yield elem

def intercalate(lst: Iterator[_T], sep: _T) -> Iterator[_T]:
    return itertools.islice(_intercalate_helper(lst, sep), 1, None, None)

def iter_replace(lst: Iterable[_T], find: _T, sub: _T) -> Iterable[_T]:
    for elem in lst:
        if elem == find:
            yield sub
        else:
            yield elem

def reverse(it: List[_T]) -> List[_T]:
    return it[::-1]
