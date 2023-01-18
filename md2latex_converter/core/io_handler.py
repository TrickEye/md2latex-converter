import json
import re

import pyperclip
from typing import Callable

from md2latex_converter.data_structures.extensions import SentExt


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


def load_extension_from_json_generator(filename: str) -> Callable[[], list[SentExt]]:
    def __r():
        _r = []
        with open(filename, 'r', encoding='utf-8') as f:
            json_str = json.loads(f.read())
        assert isinstance(json_str, list), f'Wrong json format! {json_str}'
        for _ in json_str:
            assert isinstance(_, dict) and len(_) == 1, f'Wrong json format! {_}'
            name = list(_)[0]
            regex = _[name]
            assert isinstance(name, str), f'Wrong json format! {_}'
            assert isinstance(regex, str), f'Wrong json format! {_}'
            try:
                re.compile(regex)
            except re.error:
                assert False, f'Wrong regex! {regex}'

            _r.append(SentExt(name, regex))

        return _r

    return __r