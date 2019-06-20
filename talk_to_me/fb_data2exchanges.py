from pathlib import Path
from typing import IO, Set, List, Tuple, Any, Iterable
import json
import zipfile
from unidecode import unidecode
from .util import concat, Exchange
from .sent2words import sent2words


def fb_data2exchanges(name: str, input_p: Path) -> Iterable[Exchange]:
    '''converts your Facebook data into a corpus for TALK TO ME

[Download your fb data][1] with these options:

date_range: all
format: JSON
quality: low
files:
  - posts
  - comments
  - messages

[1]: https://www.facebook.com/help/212802592074644?helpref=faq_content

incpy.memoize

    '''
        

    with zipfile.ZipFile(input_p, 'r') as input_zip:
        paths = {
            tuple(path.split('/'))
            for path in input_zip.namelist()
            if not path.endswith('/')
        }

        message_paths, media_paths, post_paths, \
            comment_paths, other_paths = sort_paths(paths)

        for path in message_paths:
            yield from message2exchanges(
                name, json.load(input_zip.open('/'.join(path)))
            )


def sort_paths(paths: Set[Tuple[str, ...]]) -> Tuple[Set[Tuple[str, ...]], ...]:
    message_paths = set()
    media_paths = set()
    post_paths = set()
    comment_paths = set()
    other_paths = set()
    for path in paths:
        if path[0] == 'messages':
            if path[1] == 'stickers_used':
                media_paths.add(path)
            elif path[1] == 'inbox':
                if path[3] in {'audio', 'gifs', 'files', 'photos', 'videos'}:
                    media_paths.add(path)
                elif path[-1].endswith('.json'):
                    message_paths.add(path)
            elif path[1] in {'filtered_threads', 'archived_threads'}:
                if path[-1].endswith('.json'):
                    message_paths.add(path)
            elif path[1] == 'message_requests':
                message_paths.add(path)
        elif path[0] == 'posts' and path[-1].endswith('.json'):
            post_paths.add(path)
        elif path[0] == 'comments' and path[-1].endswith('.json'):
            comment_paths.add(path)
        elif path[0] == 'photos_and_videos':
            other_paths.add(path)

    unused_paths = paths - message_paths - media_paths - post_paths - comment_paths - other_paths
    assert not unused_paths, unused_paths

    return message_paths, media_paths, post_paths, comment_paths, other_paths


def message2exchanges(name: str, obj: Any) -> Iterable[Exchange]:
    messages = obj['messages']
    for msg1, msg2 in zip(messages[:-1], messages[1:]):
        if msg2['sender_name'] == name:
            if 'content'in msg1 and 'content' in msg2:
                # print(msg1['content'], '->', msg2['content'])
                # TODO: Stop ignoring unicode smileys ('\u263A')
                yield (
                    sent2words(unidecode(msg1['content'])),
                    sent2words(unidecode(msg2['content'])),
                )
            else:
                pass
                # print(msg1, msg2)
                # raise RuntimeError()
