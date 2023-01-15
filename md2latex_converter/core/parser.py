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

from md2latex_converter.core.inline import texify
from md2latex_converter.core.sentences import *


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


class NonTerminatingSymbol:
    @staticmethod
    def parse(tokenizer: Tokenizer):
        pass

    def toLaTeX(self):
        pass


class Document(NonTerminatingSymbol):
    components: list['Component']

    __symbol_name = 'Document'

    def __init__(self, components: list['Component']):
        self.components = components

    @staticmethod
    def parse(tokenizer: Tokenizer) -> 'Document':
        components: list['Component'] = []

        while not isinstance(tokenizer.peek, Eof):
            if (component := Component.parse(tokenizer)) is not None:
                components.append(component)

        assert isinstance(tokenizer.peek, Eof), f'expected EOF in line {tokenizer.line}'

        return Document(components)

    def toLaTeX(self) -> list[tuple[int, str]]:
        document_class: tuple[int, str] = (0, r'\documentclass{ctexart}')

        used_packages: list[tuple[int, str]] = [
            (0, r'\usepackage{graphicx}'),
            (0, r'\usepackage{hyperref}')
        ]

        title_candidates: list[Component] = list(
            filter(lambda c: isinstance(c, TitleBlock) and c.title.hierarchy == 1, self.components))

        candidate0 = title_candidates[0]
        assert isinstance(candidate0, TitleBlock)
        title_string: str = candidate0.title.title_name if len(title_candidates) == 1 else 'Your title for the article!'

        title_decl: tuple[int, str] = (0, r'\title{' + texify(title_string) + '}')

        document_begin: tuple[int, str] = (0, r'\begin{document}')

        make_title: tuple[int, str] = (1, r'\maketitle')

        components_latex: list[tuple[int, str]] = \
            [_ for component in self.components for _ in [*component.toLaTeX(), (0, '')]]

        document_end: tuple[int, str] = (0, r'\end{document}')

        return [
            document_class,
            * used_packages,
            title_decl,
            document_begin,
            make_title,
            * components_latex,
            document_end
        ]


class Component(NonTerminatingSymbol):
    __symbol_name = 'Component'

    @staticmethod
    def parse(tokenizer: Tokenizer):
        if isinstance(tokenizer.peek, Title):
            return TitleBlock.parse(tokenizer)
        elif isinstance(tokenizer.peek, Text):
            return PlainText.parse(tokenizer)
        elif isinstance(tokenizer.peek, UnorderedList):
            return ULBlock.parse(tokenizer)
        elif isinstance(tokenizer.peek, OrderedList):
            return OLBlock.parse(tokenizer)
        elif isinstance(tokenizer.peek, EmptySentence):
            tokenizer.next()
            return None
        elif isinstance(tokenizer.peek, Picture):
            return PictureImportation.parse(tokenizer)
        else:
            assert False, f'm2l did not support this sentence type {type(tokenizer.peek)}'

    def toLaTeX(self) -> list[tuple[int, str]]:
        pass


class TitleBlock(Component):
    title: Title

    __symbol_name = 'TitleBlock'
    labels: list[str] = [
        '',
        '',
        'section',
        'subsection',
        'subsubsection',
        'subsubsection',
        'subsubsection',
    ]

    def __init__(self, title: Sentence):
        assert isinstance(title, Title)
        self.title = title

    @staticmethod
    def parse(tokenizer: Tokenizer) -> 'TitleBlock':
        assert isinstance(tokenizer.peek, Title), f'missing Title in line {tokenizer.line}'

        title = tokenizer.peek
        tokenizer.next()

        return TitleBlock(title)

    def toLaTeX(self) -> list[tuple[int, str]]:
        if self.title.hierarchy == 1:
            return []
        else:
            label: str = TitleBlock.labels[self.title.hierarchy]
            return [(1, '\\' + label + '{' + texify(self.title.title_name) + '}')]


class PlainText(Component):
    texts: list[Text]
    __symbol_name = 'PlainText'

    def __init__(self, texts: list[Text]):
        self.texts = texts

    @staticmethod
    def parse(tokenizer: Tokenizer):
        texts: list[Text] = []

        assert isinstance(tokenizer.peek, Text), f'missing Text in line {tokenizer.line}'
        while isinstance((temp := tokenizer.peek), Text):
            assert isinstance(temp, Text)
            texts.append(temp)
            tokenizer.next()

        assert isinstance(tokenizer.peek, EmptySentence), f'missing EmptySentence in line {tokenizer.line}'
        while isinstance(tokenizer.peek, EmptySentence):
            tokenizer.next()

        return PlainText(texts)

    def toLaTeX(self) -> list[tuple[int, str]]:
        return [(1, ' '.join([texify(text.content.strip()) for text in self.texts]))]


class ULBlock(Component):
    listitems: list[tuple[UnorderedList, list[Text]]]

    __symbol_name = 'ULBlock'

    def __init__(self, listitems: list[tuple[UnorderedList, list[Text]]]):
        self.listitems = listitems

    @staticmethod
    def parse(tokenizer: Tokenizer) -> 'ULBlock':
        listitems: list[tuple[UnorderedList, list[Text]]] = []

        assert isinstance(tokenizer.peek, UnorderedList), f'missing UnorderedList in line {tokenizer.line}'
        while isinstance((ul := tokenizer.peek), UnorderedList):
            assert isinstance(ul, UnorderedList)
            tokenizer.next()
            texts = []
            while isinstance((text := tokenizer.peek), Text):
                assert isinstance(text, Text)
                texts.append(text)
                tokenizer.next()
            listitems.append((ul, texts))

        assert isinstance(tokenizer.peek, EmptySentence), f'missing EmptySentence in line {tokenizer.line}'
        while isinstance(tokenizer.peek, EmptySentence):
            tokenizer.next()

        return ULBlock(listitems)

    def toLaTeX(self) -> list[tuple[int, str]]:
        indent = 1

        spans: set[int] = set([_[0].whitespace_span for _ in self.listitems])
        spans: list[int] = list(spans)
        spans.sort()
        hierarchies: list[int] = [spans.index(_[0].whitespace_span) for _ in self.listitems]

        ret: list[tuple[int, str]] = [(1, r'\begin{itemize}')]
        cur: list[int] = [0]
        for _ in range(len(self.listitems)):
            if cur[-1] == hierarchies[_]:
                ret.append((indent + 1, r'\item ' + texify(' '.join(
                    [self.listitems[_][0].main_content.strip(),
                     *[k.content.strip() for k in self.listitems[_][1]]]))))
            elif cur[-1] < hierarchies[_]:
                ret.append((indent + 1, r'\begin{itemize}'))
                indent += 1
                ret.append((indent + 1, r'\item ' + texify(' '.join(
                    [self.listitems[_][0].main_content.strip(),
                     *[k.content.strip() for k in self.listitems[_][1]]]))))
                cur.append(hierarchies[_])
            elif cur[-1] > hierarchies[_]:
                while cur[-1] > hierarchies[_]:
                    cur.pop()
                    ret.append((indent, r'\end{itemize}'))
                    indent -= 1
                ret.append((indent + 1, r'\item ' + texify(' '.join(
                    [self.listitems[_][0].main_content.strip(),
                     *[k.content.strip() for k in self.listitems[_][1]]]))))
        while cur[-1] > 0:
            cur.pop()
            ret.append((indent, r'\end{itemize}'))
            indent -= 1
        ret.append((1, r'\end{itemize}'))

        return ret


class OLBlock(Component):
    listitems: list[tuple[OrderedList, list[Text]]]

    __symbol_name = 'OLBlock'

    def __init__(self, listitems: list[tuple[OrderedList, list[Text]]]):
        self.listitems = listitems

    @staticmethod
    def parse(tokenizer: Tokenizer) -> 'OLBlock':
        listitems: list[tuple[OrderedList, list[Text]]] = []

        assert isinstance(tokenizer.peek, OrderedList), f'missing OrderedList in line {tokenizer.line}'
        while isinstance((ol := tokenizer.peek), OrderedList):
            assert isinstance(ol, OrderedList)
            tokenizer.next()
            texts = []
            while isinstance((text := tokenizer.peek), Text):
                assert isinstance(text, Text)
                texts.append(text)
                tokenizer.next()
            listitems.append((ol, texts))

        assert isinstance(tokenizer.peek, EmptySentence), f'missing EmptySentence in line {tokenizer.line}'
        while isinstance(tokenizer.peek, EmptySentence):
            tokenizer.next()

        return OLBlock(listitems)

    def toLaTeX(self) -> list[tuple[int, str]]:
        indent = 1

        spans: set[int] = set([_[0].whitespace_span for _ in self.listitems])
        spans: list[int] = list(spans)
        spans.sort()
        hierarchies: list[int] = [spans.index(_[0].whitespace_span) for _ in self.listitems]

        ret: list[tuple[int, str]] = [(1, '\\begin{enumerate}')]
        cur: list[int] = [0]
        for _ in range(len(self.listitems)):
            if cur[-1] == hierarchies[_]:
                ret.append((indent + 1, '\\item ' + texify(' '.join(
                    [self.listitems[_][0].main_content.strip(),
                     *[k.content.strip() for k in self.listitems[_][1]]]))))
            elif cur[-1] < hierarchies[_]:
                ret.append((indent + 1, '\\begin{enumerate}'))
                indent += 1
                ret.append((indent + 1, '\\item ' + texify(' '.join(
                    [self.listitems[_][0].main_content.strip(),
                     *[k.content.strip() for k in self.listitems[_][1]]]))))
                cur.append(hierarchies[_])
            elif cur[-1] > hierarchies[_]:
                while cur[-1] > hierarchies[_]:
                    cur.pop()
                    ret.append((indent, '\\end{enumerate}'))
                    indent -= 1
                ret.append((indent + 1, '\\item ' + texify(' '.join(
                    [self.listitems[_][0].main_content.strip(),
                     *[k.content.strip() for k in self.listitems[_][1]]]))))
        while cur[-1] > 0:
            cur.pop()
            ret.append((indent, '\\end{enumerate}'))
            indent -= 1
        ret.append((1, '\\end{enumerate}'))

        return ret


class PictureImportation(Component):
    picture: Picture

    __symbol_name = 'PictureImportation'

    def __init__(self, picture: Picture):
        self.picture: Picture = picture

    @staticmethod
    def parse(tokenizer: Tokenizer) -> 'PictureImportation':
        assert isinstance(tokenizer.peek, Picture), f'missing Picture in line {tokenizer.line}'
        picture = tokenizer.peek
        tokenizer.next()

        assert isinstance(tokenizer.peek, EmptySentence), f'missing EmptySentence in line {tokenizer.line}'
        while isinstance(tokenizer.peek, EmptySentence):
            tokenizer.next()

        assert isinstance(picture, Picture)
        return PictureImportation(picture)

    def toLaTeX(self) -> list[tuple[int, str]]:
        ret: list[tuple[int, str]] = []
        ret.append((1, r'\begin{figure}'))
        ret.append((2, r'\includegraphics{' + self.picture.path_to_pic + '}'))
        if self.picture.alt_text is not None and self.picture.alt_text != '':
            ret.append((2, r'\caption{' + self.picture.alt_text + '}'))
        ret.append((1, r'\end{figure}'))
        return ret
