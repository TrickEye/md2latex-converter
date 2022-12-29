import re


class Sentence:
    line: int
    identifier: str
    content: str

    def __init__(self, index, identifier, content):
        self.line = index + 1
        self.identifier = identifier
        self.content = content

    def __str__(self):
        return f'@ line {self.line:<4} {self.identifier:<20} -- {self.content}'


class Title(Sentence):
    hierarchy: int

    def __init__(self, line, content):
        super().__init__(line, 'Title', content)
        self.hierarchy = len(re.match(r'(#+)', content).group())


class Text(Sentence):
    def __init__(self, line, content):
        super().__init__(line, 'Text', content)


class EmptySentence(Sentence):
    def __init__(self, line):
        super().__init__(line, 'EmptySentence', ' ')


class UnorderedList(Sentence):
    hierarchy: int
    main_content: str

    def __init__(self, line, content):
        super().__init__(line, 'UnorderedList', content)
        match = re.match(r'(\s*)[*-]\s+(.*)', content)
        self.hierarchy = len(match.group(1))
        self.main_content = match.group(2)


class OrderedList(Sentence):
    hierarchy: int
    main_content: str

    def __init__(self, line, content):
        super().__init__(line, 'OrderedList', content)
        match = re.match(r'(\s*)\d+\.\s+(.*)', content)
        self.hierarchy = len(match.group(1))
        self.main_content = match.group(2)


class Eof(Sentence):
    def __init__(self, line):
        super().__init__(line, 'EOF', '\\0')
