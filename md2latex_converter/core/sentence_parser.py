from md2latex_converter.data_structures.extensions import SentExt
from md2latex_converter.data_structures.sentences import *


def lex(input_string: str) -> list[Sentence]:
    """
    A general lexer for each line of the source .md file.

    It identifies and classifies the types of each line, converting
    them into a specific child class of the overall super class
    [md2latex_converter.sentences.Sentence]

    The lexer is based on regex. The classification rules for this project
    is listed as follows:

        [sentence.Title]:
            r'^(#){1,6}\s*(.*)$'
        [sentence.EmptySentence]:
            r'^\s*$'
        [sentence.UnorderedList]；
            r'^(\s*)[*-]\s+(.*)$'
        [sentence.OrderedList]:
            r'^(\s*)\d+\.\s+(.*)$'
        [sentence.Eof]:
            r'^\x00$'
        [sentence.Text]:
            r'^.*$'
        [sentence.Picture]

    For each line from the input, the lexer will seek the first match in the
    regexes above.
    """
    ret = []
    input_strings = input_string.split('\n')
    for _ in range(len(input_strings)):
        sentence = input_strings[_]
        for regex in SentExt.regex_map:
            if re.match(regex, sentence) is not None:
                ret.append(SentExt.regex_map[regex](_, sentence))
                break
        else:
            if re.match(r'^(#){1,6}\s*(.*)$', sentence) is not None:
                ret.append(Title(_, sentence))
            elif re.match(r'^\s*$', sentence) is not None:
                ret.append(EmptySentence(_))
            elif re.match(r'^(\s*)[*-]\s+(.*)$', sentence) is not None:
                ret.append(UnorderedList(_, sentence))
            elif re.match(r'^(\s*)\d+\.\s+(.*)$', sentence) is not None:
                ret.append(OrderedList(_, sentence))
            elif re.match(r'^\x00$', sentence) is not None:
                ret.append(Eof(_))
            elif re.match(r'^!\[(.*)]\((.+)\)', sentence) is not None:
                ret.append(Picture(_, sentence))
            elif re.match(r'^.*$', sentence) is not None:
                ret.append(Text(_, sentence))
    return ret