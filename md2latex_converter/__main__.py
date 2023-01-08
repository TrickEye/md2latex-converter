import os

from typing import List, Tuple

from md2latex_converter import inputhandler, regexlexer
from md2latex_converter.error import *
from md2latex_converter.parser import Parser, Document
from md2latex_converter.sentences import Sentence


def main(defaultfilename: str = None) -> None:
    print('md2latex converter V-0.0.5a1')

    filename, isdev = parse_command(defaultfilename)

    file_string: str = inputhandler.getfileString(filename)

    sentence_list: List[Sentence] = regexlexer.lex(file_string)

    if isdev:
        for _ in sentence_list:
            print(_)

    document: Document = Parser(sentence_list).parse()

    latexes: List[Tuple[int, str]] = document.toLaTeX()

    output_basename: str = (os.path.basename(filename)[:-3] if filename.endswith('.md') else os.path.basename(filename)) + '.tex'

    with open(output_basename, 'w', encoding='utf-8') as f:
        for _ in latexes:
            f.write('\t' * _[0] + _[1])
            f.write('\n')

    print('Done!')


def parse_command(defaultfilename: str) -> Tuple[str, bool]:
    if defaultfilename is not None:
        filename = defaultfilename
    elif len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        print('usage: m2l filename')
        print('well you can also tell me which file now. ')
        filename = input()

    isdev = sys.argv[2] == 'dev' if len(sys.argv) >= 3 else False

    return filename, isdev


if __name__ == "__main__":
    main('README.md')
