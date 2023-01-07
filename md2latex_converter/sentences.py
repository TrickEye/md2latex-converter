import re
from typing import Any


class Sentence:
    line: int
    identifier: str
    content: str

    def __init__(self, index: int, identifier: str, content: str):
        self.line = index + 1
        self.identifier = identifier
        self.content = content

    def __str__(self):
        return f'@ line {self.line:<4} {self.identifier:<20} -- {self.content}'


class Title(Sentence):
    title_name: str
    hierarchy: int

    def __init__(self, line: int, content: str):
        super().__init__(line, 'Title', content)
        self.hierarchy = len(re.match(r'(#+)', content).group())
        self.title_name = re.match(r'#+\s+(.*)$', content).group(1)


class Text(Sentence):
    def __init__(self, line: int, content: str):
        super().__init__(line, 'Text', content)


class EmptySentence(Sentence):
    def __init__(self, line: int):
        super().__init__(line, 'EmptySentence', ' ')


class UnorderedList(Sentence):
    main_content: str
    whitespace_span: int

    def __init__(self, line: int, content: str):
        super().__init__(line, 'UnorderedList', content)
        match = re.match(r'(\s*)[*-]\s+(.*)', content)

        whitespace: str = match.group(1)
        whitespace_span: int = 0
        for _ in whitespace:
            whitespace_span += 4 if _ == '\t' else 1

        self.whitespace_span = whitespace_span
        self.main_content = match.group(2)


class OrderedList(Sentence):
    whitespace_span: int
    main_content: str

    def __init__(self, line: int, content: str):
        super().__init__(line, 'OrderedList', content)
        match = re.match(r'(\s*)\d+\.\s+(.*)', content)

        whitespace = match.group(1)
        whitespace_span = 0
        for _ in whitespace:
            whitespace_span += 4 if _ == '\t' else 1

        self.whitespace_span = whitespace_span
        self.main_content = match.group(2)


class Eof(Sentence):
    def __init__(self, line):
        super().__init__(line, 'EOF', '\\0')


class Picture(Sentence):
    path_to_pic: str
    alt_text: str

    def __init__(self, line, content):
        super().__init__(line, 'Picture', content)
        match = re.match('!\[(.*)]\((.*)\)', content)
        self.alt_text = match.group(1)
        self.path_to_pic = match.group(2)
