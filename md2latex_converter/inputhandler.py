import os
import os.path

from md2latex_converter.error import FileNFError
from md2latex_converter.error import FilenameError


def readfile(filename: str) -> str:
    # path2file = os.path.abspath(filename)
    if not os.path.isfile(filename):
        raise FileNFError(filename)
    elif not filename.endswith('.md'):
        raise FilenameError(filename)

    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def getfileString(filename: str) -> str:
    try:
        file = readfile(filename)
    except FileNFError as e:
        e.handle()
    except FilenameError as e:
        e.handle()
    else:
        return file + '\0'
