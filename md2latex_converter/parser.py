"""
A general parser for markdown sentences prepared by the lexer.

Markdown Grammar used in this project is listed as follows:
    Document:
        (Component)* [sentence.eof]
    Components:
        (TitleBlock) | (PlainText) | (UnorderedList) | (OrderedList) | (PictureImportation) | [sentence.emptySentence]
    TitleBlock:
        [sentence.title]
    PlainText:
        [sentence.text]* [sentence.emptySentence]+
    UnorderedList:
        ([sentence.unorderedList] [sentence.text]* )* [sentence.emptySentence]+
    OrderedList:
        ([sentence.orderedList] [sentence.text]* )* [sentence.emptySentence]+
    PictureImportation:
        [sentence.orderedList] [sentence.emptySentence]+
"""

from md2latex_converter.error import ParseError
from md2latex_converter import sentences
from md2latex_converter.inline import texify
from md2latex_converter.sentences import Sentence, Eof, Title, Text


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
        self._peek_token = self._sentences[self._index] if self._index < self._length else sentences.Eof(self._index)
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
    __symbol_name = 'Document'

    def __init__(self, components: list['Component']):
        self.components = components

    @staticmethod
    def parse(tokenizer: Tokenizer) -> 'Document':
        components: list['Component'] = []
        while not isinstance(tokenizer.peek, sentences.Eof):
            component: Component = Component.parse(tokenizer)
            if component is not None:
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
        elif isinstance(tokenizer.peek, sentences.UnorderedList):
            return UnorderedList.parse(tokenizer)
        elif isinstance(tokenizer.peek, sentences.OrderedList):
            return OrderedList.parse(tokenizer)
        elif isinstance(tokenizer.peek, sentences.EmptySentence):
            tokenizer.next()
            return None
        elif isinstance(tokenizer.peek, sentences.Picture):
            return PictureImportation.parse(tokenizer)
        else:
            assert False, f'm2l did not support this sentence type'

    def toLaTeX(self) -> list[tuple[int, str]]:
        pass


class TitleBlock(Component):
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
        self.title: Title = title

    @staticmethod
    def parse(tokenizer: Tokenizer) -> 'TitleBlock':
        if not isinstance(tokenizer.peek, Title):
            raise ParseError(TitleBlock.__symbol_name)
        else:
            title: Sentence = tokenizer.peek
            tokenizer.next()
            return TitleBlock(title)

    def toLaTeX(self) -> list[tuple[int, str]]:
        if self.title.hierarchy == 1:
            return []
        else:
            label: str = TitleBlock.labels[self.title.hierarchy]
            return [(1, '\\' + label + '{' + texify(self.title.title_name) + '}')]


class PlainText(Component):
    __symbol_name = 'PlainText'

    def __init__(self, texts: list[sentences.Text]):
        self.texts: list[sentences.Text] = texts

    @staticmethod
    def parse(tokenizer: Tokenizer):
        texts: list[sentences.Text] = []
        if not isinstance(tokenizer.peek, sentences.Text):
            raise ParseError(PlainText.__symbol_name)
        while isinstance(tokenizer.peek, sentences.Text):
            temp = tokenizer.peek
            assert isinstance(temp, sentences.Text)
            texts.append(temp)
            tokenizer.next()
        if not isinstance(tokenizer.peek, sentences.EmptySentence):
            raise ParseError(PlainText.__symbol_name)
        while isinstance(tokenizer.peek, sentences.EmptySentence):
            tokenizer.next()
        return PlainText(texts)

    def toLaTeX(self) -> list[tuple[int, str]]:
        return [(1, texify(' '.join([text.content.strip() for text in self.texts])))]


class UnorderedList(Component):
    __symbol_name = 'UnorderedList'

    def __init__(self, listitems: list[tuple[sentences.UnorderedList, list[sentences.Text]]]):
        self.listitems: list[tuple[sentences.UnorderedList, list[sentences.Text]]] = listitems

    @staticmethod
    def parse(tokenizer: Tokenizer) -> 'UnorderedList':
        listitems: list[tuple[sentences.UnorderedList, list[sentences.Text]]] = []
        if not isinstance(tokenizer.peek, sentences.UnorderedList):
            raise ParseError(UnorderedList.__symbol_name)
        while isinstance((ul := tokenizer.peek), sentences.UnorderedList):
            assert isinstance(ul, sentences.UnorderedList)
            tokenizer.next()
            texts = []
            while isinstance((text := tokenizer.peek), sentences.Text):
                assert isinstance(text, sentences.Text)
                texts.append(text)
                tokenizer.next()
            listitems.append((ul, texts))
        if not isinstance(tokenizer.peek, sentences.EmptySentence):
            raise ParseError(UnorderedList.__symbol_name)
        while isinstance(tokenizer.peek, sentences.EmptySentence):
            tokenizer.next()
        return UnorderedList(listitems)

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


class OrderedList(Component):
    __symbol_name = 'OrderedList'

    def __init__(self, listitems: list[tuple[sentences.OrderedList, list[sentences.Text]]]):
        self.listitems: list[tuple[sentences.OrderedList, list[sentences.Text]]] = listitems

    @staticmethod
    def parse(tokenizer: Tokenizer) -> 'OrderedList':
        listitems: list[tuple[sentences.OrderedList, list[sentences.Text]]] = []
        if not isinstance(tokenizer.peek, sentences.OrderedList):
            raise ParseError(OrderedList.__symbol_name)
        while isinstance((ol := tokenizer.peek), sentences.OrderedList):
            assert isinstance(ol, sentences.OrderedList)
            tokenizer.next()
            texts = []
            while isinstance((text := tokenizer.peek), sentences.Text):
                assert isinstance(text, sentences.Text)
                texts.append(text)
                tokenizer.next()
            listitems.append((ol, texts))
        if not isinstance(tokenizer.peek, sentences.EmptySentence):
            raise ParseError(OrderedList.__symbol_name)
        while isinstance(tokenizer.peek, sentences.EmptySentence):
            tokenizer.next()
        return OrderedList(listitems)

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
    __symbol_name = 'PictureImportation'

    def __init__(self, picture: sentences.Picture):
        self.picture: sentences.Picture = picture

    @staticmethod
    def parse(tokenizer: Tokenizer) -> 'PictureImportation':
        if not isinstance(tokenizer.peek, sentences.Picture):
            raise ParseError(PictureImportation.__symbol_name)
        picture: sentences.Sentence = tokenizer.peek
        tokenizer.next()
        if not isinstance(tokenizer.peek, sentences.EmptySentence):
            raise ParseError(PictureImportation.__symbol_name)
        while isinstance(tokenizer.peek, sentences.EmptySentence):
            tokenizer.next()
        assert isinstance(picture, sentences.Picture)
        return PictureImportation(picture)

    def toLaTeX(self) -> list[tuple[int, str]]:
        ret: list[tuple[int, str]] = []
        ret.append((1, r'\begin{figure}'))
        ret.append((2, r'\includegraphics{' + self.picture.path_to_pic + '}'))
        if self.picture.alt_text is not None and self.picture.alt_text != '':
            ret.append((2, r'\caption{' + self.picture.alt_text + '}'))
        ret.append((1, r'\end{figure}'))
        return ret
