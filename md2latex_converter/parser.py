"""
A general parser for markdown sentences prepared by the lexer.

Markdown Grammar used in this project is listed as follows:
    Document:
        (Component)* [sentence.eof]
    Components:
        (Title) | (PlainText) | (UnorderedList) | (OrderedList) | [sentence.emptySentence]
    Title:
        [sentence.title]
    PlainText:
        [sentence.text]* [sentence.emptySentence]+
    UnorderedList:
        [sentence.unorderedList]* [sentence.emptySentence]+
    OrderedList:
        [sentence.orderedList]* [sentence.emptySentence]+
    PictureImportation:
        [sentence.orderedList] [sentence.emptySentence]+
"""
from md2latex_converter.error import ParseError, ListHierarchyWarning
from md2latex_converter import sentences
from md2latex_converter.inline import LaTeXEscape


class Parser:

    def __init__(self, sentences):
        self.sentences = sentences
        self.index = 0
        self.length = len(sentences)
        self.__peek_token = sentences[0]

    def peek(self):
        return self.__peek_token

    def next(self):
        self.index += 1
        self.__peek_token = self.sentences[self.index] if self.index < self.length else sentences.Eof(-1)
        return self.__peek_token

    def parse(self):
        return Document.parse(self)


class NonTerminatingSymbol:
    @staticmethod
    def parse(parser: Parser):
        pass

    def toLaTeX(self):
        pass


class Document(NonTerminatingSymbol):
    __symbol_name = 'Document'

    def __init__(self, components: ['Component']):
        self.components = components

    @staticmethod
    def parse(parser: Parser):
        components = []
        while not isinstance(parser.peek(), sentences.Eof):
            component = Component.parse(parser)
            if component is not None:
                components.append(component)
        if not isinstance(parser.peek(), sentences.Eof):
            raise ParseError(Document.__symbol_name)
        return Document(components)

    def toLaTeX(self):
        document_class = '\\documentclass{ctexart}'
        #
        # title_string = 'Your title for the article!'
        # for component in self.components:
        #     if isinstance(component, Title) and component.title.hierarchy == 1:
        #         title_string = component.title.title_name

        used_packages = [
            r'\usepackage{graphicx}',
            r'\usepackage{hyperref}'
        ]

        title_string = title_candidates[0].title.title_name \
            if len(title_candidates := list(filter(lambda c: isinstance(c, Title) and c.title.hierarchy == 1, self.components))) == 1 \
            else 'Your title for the article!'

        title_decl = '\\title{' + title_string + '}'

        document_begin = '\\begin{document}'

        maketitle = '\\maketitle'

        components_latex = []
        for component in self.components:
            if (temp := component.toLaTeX()) is not None:
                for _ in temp:
                    components_latex.append(_)
                components_latex.append('\n')

        document_end = '\\end{document}'

        return [document_class, *used_packages, title_decl, document_begin, maketitle, *components_latex, document_end]


class Component(NonTerminatingSymbol):
    __symbol_name = 'Component'

    @staticmethod
    def parse(parser: Parser):
        if isinstance(parser.peek(), sentences.Title):
            return Title.parse(parser)
        elif isinstance(parser.peek(), sentences.Text):
            return PlainText.parse(parser)
        elif isinstance(parser.peek(), sentences.UnorderedList):
            return UnorderedList.parse(parser)
        elif isinstance(parser.peek(), sentences.OrderedList):
            return OrderedList.parse(parser)
        elif isinstance(parser.peek(), sentences.EmptySentence):
            parser.next()
            return None
        elif isinstance(parser.peek(), sentences.Picture):
            return PictureImportation.parse(parser)

    def toLaTeX(self):
        pass


class Title(NonTerminatingSymbol):
    __symbol_name = 'Title'
    labels = [
        '',
        '',
        'section',
        'subsection',
        'subsubsection',
        'subsubsection',
        'subsubsection',
    ]

    def __init__(self, title: sentences.Title):
        self.title = title

    @staticmethod
    def parse(parser: Parser) -> 'Title':
        if not isinstance(parser.peek(), sentences.Title):
            raise ParseError(Title.__symbol_name)
        else:
            title = parser.peek()
            parser.next()
            return Title(title)

    def toLaTeX(self):
        if self.title.hierarchy == 1:
            return None
        else:
            label = Title.labels[self.title.hierarchy]
            return ['\\' + label + '{' + LaTeXEscape(self.title.title_name) + '}']


class PlainText(NonTerminatingSymbol):
    __symbol_name = 'PlainText'

    def __init__(self, texts: [sentences.Text]):
        self.texts = texts

    @staticmethod
    def parse(parser: Parser):
        texts = []
        if not isinstance(parser.peek(), sentences.Text):
            raise ParseError(PlainText.__symbol_name)
        while isinstance(parser.peek(), sentences.Text):
            texts.append(parser.peek())
            parser.next()
        if not isinstance(parser.peek(), sentences.EmptySentence):
            raise ParseError(PlainText.__symbol_name)
        while isinstance(parser.peek(), sentences.EmptySentence):
            parser.next()
        return PlainText(texts)

    def toLaTeX(self):
        return [LaTeXEscape(text.content) for text in self.texts]


class UnorderedList(NonTerminatingSymbol):
    __symbol_name = 'UnorderedList'

    def __init__(self, listitems: [sentences.UnorderedList]):
        self.listitems = listitems

    @staticmethod
    def parse(parser: Parser):
        listitems = []
        if not isinstance(parser.peek(), sentences.UnorderedList):
            raise ParseError(UnorderedList.__symbol_name)
        while isinstance(parser.peek(), sentences.UnorderedList):
            listitems.append(parser.peek())
            parser.next()
        if not isinstance(parser.peek(), sentences.EmptySentence):
            raise ParseError(UnorderedList.__symbol_name)
        while isinstance(parser.peek(), sentences.EmptySentence):
            parser.next()
        return UnorderedList(listitems)

    def toLaTeX(self):
        spans = set([_.whitespace_span for _ in self.listitems])
        spans = list(spans)
        spans.sort()
        hierarchies = [spans.index(_.whitespace_span) for _ in self.listitems]

        ret = ['\\begin{itemize}']
        cur = [0]
        for _ in range(len(self.listitems)):
            if cur[-1] == hierarchies[_]:
                ret.append('\\item ' + LaTeXEscape(self.listitems[_].main_content))
            elif cur[-1] < hierarchies[_]:
                ret.append('\\begin{itemize}')
                ret.append('\\item ' + LaTeXEscape(self.listitems[_].main_content))
                cur.append(hierarchies[_])
            elif cur[-1] > hierarchies[_]:
                while cur[-1] > hierarchies[_]:
                    cur.pop()
                    ret.append('\\end{itemize}')
                ret.append('\\item ' + LaTeXEscape(self.listitems[_].main_content))
        while cur[-1] > 0:
            cur.pop()
            ret.append('\\end{itemize}')
        ret.append('\\end{itemize}')

        return ret


class OrderedList(NonTerminatingSymbol):
    __symbol_name = 'OrderedList'

    def __init__(self, listitems):
        self.listitems = listitems

    @staticmethod
    def parse(parser: Parser):
        listitems = []
        if not isinstance(parser.peek(), sentences.OrderedList):
            raise ParseError(OrderedList.__symbol_name)
        while isinstance(parser.peek(), sentences.OrderedList):
            listitems.append(parser.peek())
            parser.next()
        if not isinstance(parser.peek(), sentences.EmptySentence):
            raise ParseError(OrderedList.__symbol_name)
        while isinstance(parser.peek(), sentences.EmptySentence):
            parser.next()
        return OrderedList(listitems)

    def toLaTeX(self):
        spans = set([_.whitespace_span for _ in self.listitems])
        spans = list(spans)
        spans.sort()
        hierarchies = [spans.index(_.whitespace_span) for _ in self.listitems]

        ret = ['\\begin{enumerate}']
        cur = [0]
        for _ in range(len(self.listitems)):
            if cur[-1] == hierarchies[_]:
                ret.append('\\item ' + LaTeXEscape(self.listitems[_].main_content))
            elif cur[-1] < hierarchies[_]:
                ret.append('\\begin{enumerate}')
                ret.append('\\item ' + LaTeXEscape(self.listitems[_].main_content))
                cur.append(hierarchies[_])
            elif cur[-1] > hierarchies[_]:
                while cur[-1] > hierarchies[_]:
                    cur.pop()
                    ret.append('\\end{enumerate}')
                ret.append('\\item ' + LaTeXEscape(self.listitems[_].main_content))
        while cur[-1] > 0:
            cur.pop()
            ret.append('\\end{enumerate}')
        ret.append('\\end{enumerate}')

        return ret


class PictureImportation(NonTerminatingSymbol):
    __symbol_name = 'PictureImportation'

    def __init__(self, picture: sentences.Picture):
        self.picture = picture

    @staticmethod
    def parse(parser: Parser):
        if not isinstance(parser.peek(), sentences.Picture):
            raise ParseError(PictureImportation.__symbol_name)
        picture = parser.peek()
        parser.next()
        if not isinstance(parser.peek(), sentences.EmptySentence):
            raise ParseError(PictureImportation.__symbol_name)
        return PictureImportation(picture)

    def toLaTeX(self):
        ret = []
        ret.append('\\begin{figure}')
        ret.append('\\includegraphics{' + self.picture.path_to_pic + '}')
        if self.picture.alt_text is not None and self.picture.alt_text != '':
            ret.append('\\caption{' + self.picture.alt_text + '}')
        ret.append('\\end{figure}')
        return ret

