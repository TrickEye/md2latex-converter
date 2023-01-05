import os

from md2latex_converter import inputhandler, regexlexer
from md2latex_converter.error import *
from md2latex_converter.parser import Parser


def main(defaultfilename: str = None) -> None:
    print('hello world, this is md2latex converter!')

    filename, isdev = parse_command(defaultfilename)

    file_string = inputhandler.getfileString(filename)

    sentence_list = regexlexer.lex(file_string)

    if isdev:
        for _ in sentence_list:
            print(_)

    document = Parser(sentence_list).parse()

    latexes = document.toLaTeX()

    output_basename = (os.path.basename(filename)[:-3] if filename.endswith('.md') else os.path.basename(filename)) + '.tex'

    with open(output_basename, 'w', encoding='utf-8') as f:
        for _ in latexes:
            f.write(_)
            f.write('\n')

    print('Done!')


def parse_command(defaultfilename: str) -> tuple[str, bool]:
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
    main('testfile.md')
