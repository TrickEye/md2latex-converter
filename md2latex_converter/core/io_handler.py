import json

import pyperclip
from typing import Callable


def read_from_file_generator(filename: str) -> Callable[[], str]:
    def _r():
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read() + '\n\n\n\0'

    return _r


def read_from_pastebin() -> str:
    s = pyperclip.paste()
    return s + '\n\n\n\0'


def write_to_file_generator(filename: str) -> Callable[[str], None]:
    def _r(s):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(s)

    return _r


def write_to_pastebin(s) -> None:
    pyperclip.copy(s)


def write_to_stdout(s) -> None:
    print(s)


def load_sent_ext_from_json_generator(filename: str) -> Callable[[], list]:
    def __r():
        with open(filename, 'r', encoding='utf-8') as f:
            json_obj = json.loads(f.read())
        assert isinstance(json_obj, list), f'Wrong json format! {json_obj}'

        return json_obj

    return __r


def load_blk_ext_from_json_generator(filename: str) -> Callable[[], list]:
    def __r():
        _r = []
        with open(filename, 'r', encoding='utf-8') as f:
            json_obj = json.loads(f.read())
        assert isinstance(json_obj, list), f'Wrong json format! Expect a list but get {json_obj}'

        return json_obj

    return __r
