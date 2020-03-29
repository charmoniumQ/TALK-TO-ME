from pathlib import Path
from typing import Set, Tuple, Any, Iterable
import json
import zipfile

# from unidecode import unidecode
from .util import concat, Exchange


def fb_data2exchanges(name: str, input_p: Path) -> Iterable[Exchange]:
    with zipfile.ZipFile(input_p, "r") as input_zip:
        paths = {
            tuple(path.split("/"))
            for path in input_zip.namelist()
            if not path.endswith("/")
        }

        (
            message_paths,
            _media_paths,
            _post_paths,
            _comment_paths,
            _other_paths,
        ) = sort_paths(paths)

        def path2exchanges(path: Iterable[str]) -> Iterable[Exchange]:
            file_bytes = input_zip.read("/".join(path))
            yield from message2exchanges(name, json.loads(file_bytes))

        return list(concat(map(path2exchanges, message_paths)))


def sort_paths(paths: Set[Tuple[str, ...]],) -> Tuple[Set[Tuple[str, ...]], ...]:
    message_paths = set()
    media_paths = set()
    post_paths = set()
    comment_paths = set()
    other_paths = set()
    for path in paths:
        if path[0] == "messages":
            if path[1] == "stickers_used":
                media_paths.add(path)
            elif path[1] == "inbox":
                if path[3] in {"audio", "gifs", "files", "photos", "videos"}:
                    media_paths.add(path)
                elif path[-1].endswith(".json"):
                    message_paths.add(path)
            elif path[1] in {"filtered_threads", "archived_threads"}:
                if path[-1].endswith(".json"):
                    message_paths.add(path)
            elif path[1] == "message_requests":
                message_paths.add(path)
        elif path[0] == "posts" and path[-1].endswith(".json"):
            post_paths.add(path)
        elif path[0] == "comments" and path[-1].endswith(".json"):
            comment_paths.add(path)
        elif path[0] == "photos_and_videos":
            other_paths.add(path)

    unused_paths = (
        paths - message_paths - media_paths - post_paths - comment_paths - other_paths
    )
    assert not unused_paths, unused_paths

    return message_paths, media_paths, post_paths, comment_paths, other_paths


def normalize_str(string: str) -> str:
    try:
        # Try changing the encoding at file-read time.
        # That doesn't fix it for some reason.
        string = string.encode("latin-1").decode("utf-8")
    except UnicodeEncodeError:
        pass
    except UnicodeDecodeError:
        # Uncomment to debug
        # print(repr(string))
        pass

    # I can also replace smart quotes with real quotes
    # The apostrophe is necessary because half of people use real apostrophes
    string = (
        string.replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2013", "-")
    )

    return string


def message2exchanges(name: str, obj: Any) -> Iterable[Exchange]:
    messages = sorted(obj["messages"], key=lambda message: message["timestamp_ms"])
    for msg1, msg2 in zip(messages[:-1], messages[1:]):
        if msg2["sender_name"] == name:
            if "content" in msg1 and "content" in msg2:
                msg1["content"] = normalize_str(msg1["content"])
                msg2["content"] = normalize_str(msg2["content"])

                # Uncomment to manually review decoding
                # if unidecode(msg1['content']) != msg1['content'] \
                #     or unidecode(msg2['content']) != msg2['content']:
                #     print(msg1['sender_name'], repr(msg1['content']))
                #     print(msg2['sender_name'], repr(msg2['content']))
                #     input()

                yield (
                    msg1["content"],
                    msg2["content"],
                )
