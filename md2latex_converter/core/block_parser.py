"""
A general parser for markdown sentences prepared by the lexer.

Markdown Grammar used in this project is listed as follows:
    Document:
        (Component)* [sentence.eof]
    Components:
        (TitleBlock) | (PlainText) | (ULBlock) | (OLBlock) | (PictureImportation) | [sentence.emptySentence]
    TitleBlock:
        [sentence.title]
    PlainText:
        [sentence.text]* [sentence.emptySentence]+
    ULBlock:
        ([sentence.unorderedList] [sentence.text]* )* [sentence.emptySentence]+
    OLBlock:
        ([sentence.orderedList] [sentence.text]* )* [sentence.emptySentence]+
    PictureImportation:
        [sentence.orderedList] [sentence.emptySentence]+
"""

from md2latex_converter.data_structures.blocks import Document
from md2latex_converter.data_structures.sentences import *


class Tokenizer:

    _sentences: list[Sentence]
    _index: int
    _length: int
    _peek_token: Sentence

    def __init__(self, _sentences: list[Sentence]):
        self._sentences = _sentences
        self._index = 0
        self._length = len(_sentences)
        self._peek_token = _sentences[0]

    @property
    def peek(self) -> Sentence:
        return self._peek_token

    def next(self) -> Sentence:
        self._index += 1
        self._peek_token = self._sentences[self._index] if self._index < self._length else Eof(self._index)
        return self._peek_token

    @property
    def line(self) -> int:
        return self._index + 1

    def parse(self) -> 'Document':
        return Document.parse(self)


