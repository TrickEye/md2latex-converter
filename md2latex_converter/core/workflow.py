from typing import Callable

from md2latex_converter.core import sentence_parser
from md2latex_converter.core.tokenizer import Tokenizer
from md2latex_converter.data_structures.blocks import Document
from md2latex_converter.data_structures import sent_ext, blk_ext


def worker_generator(
        sent_ext_handler: Callable[[], list],
        blk_ext_handler: Callable[[], list],
        provider: Callable[[], str],
        consumers: list[Callable[[str], None]]
) -> Callable[[], None]:
    def _r():
        sent_ext_src = sent_ext_handler()
        sent_ext.register(sent_ext_src)
        blk_ext_src = blk_ext_handler()
        blk_ext.register(blk_ext_src)

        src = provider()
        sentence_list = sentence_parser.lex(src)
        tokenizer = Tokenizer(sentence_list)
        document = Document.parse(tokenizer)
        latexes = document.toLaTeX()
        tar = ''.join([('\t' * _[0] + _[1] + '\n') for _ in latexes])

        for _ in consumers:
            _(tar)

    return _r
