import sys
from typing import Type

from md2latex_converter.core.inline import texify
from md2latex_converter.data_structures.runtime_maps import EXTENDED_PREFIX_BLOCK_MAP
from md2latex_converter.data_structures.prototypes import Block
from md2latex_converter.data_structures.sentences import *


class Document(Block):
    components: list['Component']

    __symbol_name = 'Document'

    def __init__(self, components: list['Component']):
        self.components = components

    @staticmethod
    def parse(tokenizer) -> 'Document':
        components: list['Component'] = []

        while not isinstance(tokenizer.peek, Eof):
            if (component := Component.parse(tokenizer)) is not None:
                components.append(component)

        assert isinstance(tokenizer.peek, Eof), f'expected EOF in line {tokenizer.line}'

        return Document(components)

    def toLaTeX(self) -> list[tuple[int, str]]:
        declarations = [
            (0, f'% Powered by markdown2latex-converter'),
            (0, f'% Invoked by command: {sys.argv}')
        ]

        document_class: tuple[int, str] = (0, r'\documentclass{ctexart}')

        used_packages: list[tuple[int, str]] = [
            (0, r'\usepackage{graphicx}'),
            (0, r'\usepackage{hyperref}')
        ]

        title_candidates: list[Component] = list(
            filter(lambda c: isinstance(c, TitleBlock) and c.title.hierarchy == 1, self.components))

        if len(title_candidates) == 1:
            candidate0 = title_candidates[0]
            assert isinstance(candidate0, TitleBlock)
            title_string: str = candidate0.title.title_name
        else:
            title_string = 'Your title for the article!'

        title_decl: tuple[int, str] = (0, r'\title{' + texify(title_string) + '}')

        document_begin: tuple[int, str] = (0, r'\begin{document}')

        make_title: tuple[int, str] = (1, r'\maketitle')

        components_latex: list[tuple[int, str]] = \
            [_ for component in self.components for _ in [*component.toLaTeX(), (0, '')]]

        indented_components_latex = \
            [(indent + 1, content) for indent, content in components_latex]

        document_end: tuple[int, str] = (0, r'\end{document}')

        return [
            *declarations,
            document_class,
            *used_packages,
            title_decl,
            document_begin,
            make_title,
            *indented_components_latex,
            document_end
        ]


class Component(Block):
    __symbol_name = 'Component'

    @staticmethod
    def parse(tokenizer):
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
        elif type(tokenizer.peek) in EXTENDED_PREFIX_BLOCK_MAP:
            return EXTENDED_PREFIX_BLOCK_MAP[type(tokenizer.peek)].parse(tokenizer)
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
    def parse(tokenizer) -> 'TitleBlock':
        assert isinstance(tokenizer.peek, Title), f'missing Title in line {tokenizer.line}'

        title = tokenizer.peek
        tokenizer.next()

        return TitleBlock(title)

    def toLaTeX(self) -> list[tuple[int, str]]:
        if self.title.hierarchy == 1:
            return []
        else:
            label: str = TitleBlock.labels[self.title.hierarchy]
            return [(0, '\\' + label + '{' + texify(self.title.title_name) + '}')]


class PlainText(Component):
    texts: list[Text]
    __symbol_name = 'PlainText'

    def __init__(self, texts: list[Text]):
        self.texts = texts

    @staticmethod
    def parse(tokenizer):
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
        return [(0, ' '.join([texify(text.content.strip()) for text in self.texts]))]


class ULBlock(Component):
    listitems: list[tuple[UnorderedList, list[Text]]]

    __symbol_name = 'ULBlock'

    def __init__(self, listitems: list[tuple[UnorderedList, list[Text]]]):
        self.listitems = listitems

    @staticmethod
    def parse(tokenizer) -> 'ULBlock':
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
        indent = 0

        spans: set[int] = set([_[0].whitespace_span for _ in self.listitems])
        spans: list[int] = list(spans)
        spans.sort()
        hierarchies: list[int] = [spans.index(_[0].whitespace_span) for _ in self.listitems]

        ret: list[tuple[int, str]] = [(0, r'\begin{itemize}')]
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
        ret.append((0, r'\end{itemize}'))

        return ret


class OLBlock(Component):
    listitems: list[tuple[OrderedList, list[Text]]]

    __symbol_name = 'OLBlock'

    def __init__(self, listitems: list[tuple[OrderedList, list[Text]]]):
        self.listitems = listitems

    @staticmethod
    def parse(tokenizer) -> 'OLBlock':
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
        indent = 0

        spans: set[int] = set([_[0].whitespace_span for _ in self.listitems])
        spans: list[int] = list(spans)
        spans.sort()
        hierarchies: list[int] = [spans.index(_[0].whitespace_span) for _ in self.listitems]

        ret: list[tuple[int, str]] = [(0, '\\begin{enumerate}')]
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
        ret.append((0, '\\end{enumerate}'))

        return ret


class PictureImportation(Component):
    picture: Picture

    __symbol_name = 'PictureImportation'

    def __init__(self, picture: Picture):
        self.picture: Picture = picture

    @staticmethod
    def parse(tokenizer) -> 'PictureImportation':
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
        ret.append((0, r'\begin{figure}'))
        ret.append((1, r'\includegraphics{' + self.picture.path_to_pic + '}'))
        if self.picture.alt_text is not None and self.picture.alt_text != '':
            ret.append((1, r'\caption{' + self.picture.alt_text + '}'))
        ret.append((0, r'\end{figure}'))
        return ret


BUILTIN_NAME_BLOCK_MAP: dict[str, Type[Block]] = {
    'Component': Component,
    'Document': Document,
    'TitleBlock': TitleBlock,
    'OLBlock': OLBlock,
    'ULBlock': ULBlock,
    'PlainText': PlainText,
    'PictureImportation': PictureImportation,
}

BUILTIN_PREFIX_BLOCK_MAP: dict[type, Type[Component]] = {
    Title: TitleBlock,
    OrderedList: OLBlock,
    UnorderedList: ULBlock,
    Text: PlainText,
    Picture: PictureImportation,
    EmptySentence: None
}
