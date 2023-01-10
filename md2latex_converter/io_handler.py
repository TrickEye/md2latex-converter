import sys
from typing import Callable


def read_from_file_generator(filename: str) -> Callable[[], str]:
    def _r():
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()

    return _r


def read_from_pastebin() -> str:
    if sys.platform.startswith('win32'):
        import win32clipboard
        win32clipboard.OpenClipboard()
        s = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return s
    else:
        assert False, f'reading from pastebin on your OS platform is not supported'


def write_to_file_generator(filename: str) -> Callable[[str], None]:
    def _r(s):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(s)

    return _r


def write_to_pastebin(s) -> None:
    if sys.platform.startswith('win32'):
        import win32clipboard
        win32clipboard.OpenClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, s)
    else:
        assert False, f'write to clipboard on your OS platform is not supported'


def write_to_stdout(s) -> None:
    print(s)
