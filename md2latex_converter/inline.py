import re


def LaTeXEscape(content: str):
    bolded = False
    italic = False
    inline_code = False

    i, l = 0, len(content)
    buffer = ''
    while i < l:
        if content.startswith(('__', '**'), i):
            buffer += '\\textbf{' if not bolded else '}'
            bolded = not bolded
            i += 2
        elif content.startswith('_', i):
            buffer += '\\textit{' if not italic else '}'
            italic = not italic
            i += 1
        elif content.startswith('`', i):
            buffer += '\\texttt{' if not inline_code else '}'
            inline_code = not inline_code
            i += 1
        elif (match := re.match('\[(.+)]\((.*)\)', content[i:])) is not None:
            buffer += '\\href{' + match.group(2) + '}{' + match.group(1) + '}'
            i += len(match.group())
        else:
            buffer += content[i]
            i += 1

    return buffer
