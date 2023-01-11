from typing import Callable

from md2latex_converter import regexlexer
from md2latex_converter.parser import Parser


def process(s):
    sentences_list = regexlexer.lex(s)
    document = Parser(sentences_list).parse()
    latexes = document.toLaTeX()
    result = ''.join([('\t' * _[0] + _[1] + '\n') for _ in latexes])
    return result


def worker_generator(provider: Callable[[], str], consumers: list[Callable[[str], None]]) -> Callable[[], None]:
    def _r():
        src = provider()
        tar = process(src)
        map(lambda _: _(tar), consumers)
        # for _ in consumers:
        #     _(tar)

    return _r
