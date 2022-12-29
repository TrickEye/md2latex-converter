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
"""
from md2latex_converter.error import ParseError
from md2latex_converter import sentences


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
        self.__peek_token = self.sentences[self.index] if self.index < self.length else Eof(-1)
        return self.__peek_token

    def parse(self):
        return Document.parse(self)


class NonTerminatingSymbol:
    @staticmethod
    def parse(parser: Parser):
        pass


class Document(NonTerminatingSymbol):
    __symbol_name = 'Document'

    def __init__(self, components):
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


class Component(NonTerminatingSymbol):
    __symbol_name = 'Component'

    def __init__(self, component: 'Component'):
        self.whoami = component

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


class Title(NonTerminatingSymbol):
    __symbol_name = 'Title'

    def __init__(self, title):
        self.title = title

    @staticmethod
    def parse(parser: Parser) -> 'Title':
        if not isinstance(parser.peek(), sentences.Title):
            raise ParseError(Title.__symbol_name)
        else:
            title = parser.peek()
            parser.next()
            return Title(title)


class PlainText(NonTerminatingSymbol):
    __symbol_name = 'PlainText'

    def __init__(self, texts):
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


class UnorderedList(NonTerminatingSymbol):
    __symbol_name = 'UnorderedList'

    def __init__(self, listitems):
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
        return UnorderedList(listitems)


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
        return OrderedList(listitems)