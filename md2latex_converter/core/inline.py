import re


def texify(content: str) -> str:
    bolded: bool | str = False
    italic: bool = False
    inline_code: bool = False

    i, l = 0, len(content)
    buffer: str = ''
    while i < l:
        if content.startswith('__', i) and (bolded or content.count('__', i + 1) != 0):
            buffer += '\\textbf{' if not bolded else '}'
            bolded = '__' if not bolded else False
            i += 2
        if content.startswith('**', i) and (bolded or content.count('**', i + 1) != 0):
            buffer += '\\textbf{' if not bolded else '}'
            bolded = '**' if not bolded else False
            i += 2
        elif content.startswith('_', i) and (italic or content.count('_', i + 1) != 0):
            buffer += '\\textit{' if not italic else '}'
            italic = not italic
            i += 1
        elif content.startswith('`', i) and (inline_code or content.count('`', i + 1) != 0):
            buffer += '\\texttt{' if not inline_code else '}'
            inline_code = not inline_code
            i += 1
        elif (match := re.match('\[(.+?)]\((.*?)\)', content[i:])) is not None:
            buffer += '\\href{' + match.group(2) + '}{' + match.group(1) + '}'
            i += len(match.group())
        else:
            buffer += content[i]
            i += 1

    return buffer
