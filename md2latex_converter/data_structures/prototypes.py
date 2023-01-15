from md2latex_converter.core.block_parser import Tokenizer


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


class Block:
    @staticmethod
    def parse(tokenizer: Tokenizer):
        pass

    def toLaTeX(self) -> list[tuple[int, str]]:
        pass

    def __str__(self):
        return ''.join([('\t' * _[0] + _[1] + '\n') for _ in self.toLaTeX()])
