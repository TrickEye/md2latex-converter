import sys


class LocaleError(BaseException):
    def handle(self):
        pass


class LocaleWarning(RuntimeWarning):
    def handle(self):
        pass


class FileNFError(LocaleError):
    def __init__(self, filename):
        super()
        self.filename = filename

    def handle(self):
        print(f'Given filename \'{self.filename}\' does not seem to be a proper file.')
        sys.exit('Fatal error! Please see above for more information.')


class FilenameError(LocaleWarning):
    def __init__(self, filename):
        self.filename = filename

    def handle(self):
        print(f'Warning. The given filename \'{self.filename}\' does not seem to be a markdown file.')


class ParseError(LocaleError):
    def __init__(self, symbol_name):
        self.symbol_name = symbol_name

    def handle(self):
        print(f'Fatal error! An error occurred while parsing {self.symbol_name}')
        sys.exit(1)
