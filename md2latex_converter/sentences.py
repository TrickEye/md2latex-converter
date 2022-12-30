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

    def __init__(self, line, content):
        super().__init__(line, 'Title', content)
        self.hierarchy = len(re.match(r'(#+)', content).group())
        self.title_name = re.match(r'#+\s+(.*)$', content).group(1)
        # print('titlename is ' + self.title_name)


class Text(Sentence):
    def __init__(self, line, content):
        super().__init__(line, 'Text', content)


class EmptySentence(Sentence):
    def __init__(self, line):
        super().__init__(line, 'EmptySentence', ' ')


class UnorderedList(Sentence):

    def __init__(self, line, content):
        super().__init__(line, 'UnorderedList', content)
        match = re.match(r'(\s*)[*-]\s+(.*)', content)

        whitespace = match.group(1)
        whitespace_span = 0
        for _ in whitespace:
            whitespace_span += 4 if _ == '\t' else 1

        self.whitespace_span = whitespace_span
        self.main_content = match.group(2)


class OrderedList(Sentence):
    hierarchy: int
    main_content: str

    def __init__(self, line, content):
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
