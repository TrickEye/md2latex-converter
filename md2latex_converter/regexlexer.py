from md2latex_converter.sentences import *


def lex(input_string: str) -> [str]:
    ret = []
    input_strings = input_string.split('\n')
    for _ in range(len(input_strings)):
        sentence = input_strings[_]
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
        elif re.match(r'^.*$', sentence) is not None:
            ret.append(Text(_, sentence))
    return ret
