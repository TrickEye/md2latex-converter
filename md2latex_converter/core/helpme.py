from md2latex_converter.version import VERSION


def handler():
    help_strs = [
        f'm2l - Markdown to LaTeX Converter, version {VERSION}',
        r'',
        r'Usage:',
        r'  m2l path/to/input_file.md [options]',
        r'  m2l pastebin [options]',
        r'  m2l help',
        r'  m2l configure',
        r'',
        r'----------------------------------------------------------------------------',
        r'File mode:',
        r'  Read from a file and compile to latex. Basic command composition:',
        r'',
        r'    m2l path/to/input_file.md [options]',
        r'',
        r'  The file path/to/input_file.md will be read. The target LaTeX file',
        r'  will be generated at input_file.tex at the current working dir',
        r'',
        r'',
        r'Pastebin mode:',
        r'  Read from pastebin and compile to latex. Basic command composition:',
        r'',
        r'    m2l -pb [options]',
        r'',
        r'  After compilation, target code will be copied into the pastebin.',
        r'  Target file path to save will be determined by a dialog window or prompt.',
        r'  The dialog can be closed, in which case no output file is produced.',
        r'',
        r'----------------------------------------------------------------------------',
        r'Possible options include:',
        r'',
        r'  -o path/to/output_file.tex',
        r'',
        r'    Replace the default target file location with path/to/output_file.tex .',
        r'    This option will also supress the dialog in pastebin mode.'
        r'',
        r'',
        r'  -stdout (or -print)',
        r'',
        r'    Print to stdout as well after compilation.'
    ]
    for _ in help_strs:
        print(_)


if __name__ == '__main__':
    handler()
