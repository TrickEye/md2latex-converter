from md2latex_converter import inputhandler, regexlexer
from md2latex_converter.error import *
from md2latex_converter.parser import Parser


def main(defaultfilename: str = None) -> None:
    print('hello world, this is md2latex converter!')

    filename = getfilename(defaultfilename)

    file_string = inputhandler.getfileString(filename)

    sentence_list = regexlexer.lex(file_string)

    document = Parser(sentence_list).parse()

    latex = document.toLaTeX()

    with open('output.tex', 'w', encoding='utf-8') as f:
        f.write(latex)

    print('Done!')


def getfilename(defaultfilename: str) -> str:
    if defaultfilename is not None:
        filename = defaultfilename
    elif len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        print('usage: m2l filename')
        print('well you can also tell me which file now. ')
        filename = input()
    return filename


if __name__ == "__main__":
    main('testfile.md')
