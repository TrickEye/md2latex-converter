from md2latex_converter import inputhandler, regexlexer
from md2latex_converter.error import *


def main(defaultfilename: str = None) -> None:
    print('hello world, this is md2latex converter!')

    filename = getfilename(defaultfilename)

    file_string = inputhandler.getfileString(filename)

    sentence_list = regexlexer.lex(file_string)

    for _ in sentence_list:
        print(_)


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
    # print(os.listdir())
    # print(os.path.abspath('filename.md'))
    main('testfile.md')
