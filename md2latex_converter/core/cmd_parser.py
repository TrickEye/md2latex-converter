import os
import sys
from typing import Callable, List


from md2latex_converter.core.configure_handler import config
from md2latex_converter.core.helpme_handler import handler
from md2latex_converter.core.workflow import worker_generator


def _warn_ifnot(expr, s):
    if not expr:
        print('Warning! ' + s, file=sys.stderr)
        sys.stderr.flush()


class Cmd:
    handler: Callable[[], None]
    output_to_stdout: bool
    help_me: bool
    configure: bool
    input_from_pastebin: bool
    output_filename: str | None
    input_filename: str | None

    def __init__(self,
                 input_filename: str | None,
                 output_filename: str | None,
                 input_from_pastebin: bool,
                 configure: bool,
                 help_me: bool,
                 output_to_stdout: bool,
                 extension_filename: str = ''
                 ):
        assert not (configure and (input_filename or output_filename or input_from_pastebin or help_me or output_to_stdout or extension_filename)), \
            '"m2l configure" does not accept other arguments.'
        assert not (help_me and (input_filename or output_filename or input_from_pastebin or configure or output_to_stdout or extension_filename)), \
            '"m2l help" does not accept other arguments.'
        assert not (input_filename and input_from_pastebin), \
            '"m2l" does not support multiple sources of input.'

        if input_filename:  # read a file and compile it to tex
            assert isinstance(input_filename, str), \
                'input file name not given!'
            assert os.path.isfile(input_filename), \
                f'{input_filename} not found'
            _warn_ifnot(input_filename.endswith('.md'),
                        f'input file name {input_filename} does not seem to be a MarkDown file.')

            if output_filename is None or output_filename == '':
                output_filename = os.path.basename(input_filename)
                if output_filename.endswith('.md'):
                    output_filename = output_filename[:-3] + '.tex'
                else:
                    output_filename = output_filename + '.tex'
            else:
                _warn_ifnot(output_filename.endswith('.tex'),
                            f'output file name {output_filename} does not seem to be a LaTeX file.')
            _warn_ifnot(not os.path.exists(output_filename) or os.path.isfile(output_filename),
                        f'{output_filename} exists and is not a file.')
            _warn_ifnot(not os.path.isfile(output_filename),
                        f'{output_filename} exists and will be overwritten.')

        if input_from_pastebin:  # read from pastebin and compile it to tex
            if output_filename is None or output_filename == '':
                try:
                    from tkinter import filedialog
                    output_filename = filedialog.asksaveasfilename()
                except ModuleNotFoundError:
                    output_filename = input('Please provide a filename, or cancel by pressing ENTER:')
            if output_filename is not None and output_filename != '':
                _warn_ifnot(output_filename.endswith('.tex'),
                            f'output file name {output_filename} does not seem to be a LaTeX file.')
                _warn_ifnot(not os.path.exists(output_filename) or os.path.isfile(output_filename),
                            f'{output_filename} exists and is not a file.')
                _warn_ifnot(not os.path.isfile(output_filename),
                            f'{output_filename} exists and will be overwritten.')

        self.input_filename = input_filename
        self.output_filename = output_filename
        self.input_from_pastebin = input_from_pastebin
        self.configure = configure
        self.help_me = help_me
        self.output_to_stdout = output_to_stdout
        self.extension_filename = extension_filename

        if self.configure:
            self.handler = config
        elif self.help_me:
            self.handler = handler
        else:
            self.handler = worker_generator(self._extension_handler, self._provider, self._consumer)

    def __str__(self):
        if self.configure:
            return 'm2l configure'
        elif self.help_me:
            return 'm2l help'
        elif self.input_filename:
            return f'm2l {self.input_filename} -o {self.output_filename}'
        elif self.input_from_pastebin:
            if self.output_filename is None:
                return f'm2l -pb'
            else:
                return f'm2l -pb -o {self.output_filename}'

    @property
    def _extension_handler(self) -> Callable[[], list]:
        from md2latex_converter.core import io_handler
        if self.extension_filename is not None and self.extension_filename != '':
            return io_handler.load_extension_from_json_generator(self.extension_filename)
        else:
            return lambda: []

    @property
    def _consumer(self) -> List[Callable[[str], None]]:
        from md2latex_converter.core import io_handler
        _r: List[Callable[[str], None]] = []
        if self.output_filename is not None and self.output_filename != '':
            _r.append(io_handler.write_to_file_generator(self.output_filename))
        if self.input_from_pastebin:
            _r.append(io_handler.write_to_pastebin)
        if self.output_to_stdout:
            _r.append(io_handler.write_to_stdout)
        return _r

    @property
    def _provider(self) -> Callable[[], str]:
        from md2latex_converter.core import io_handler
        if self.input_filename:
            return io_handler.read_from_file_generator(self.input_filename)
        else:
            return io_handler.read_from_pastebin


def parse_command() -> Cmd:
    return _parse_command(sys.argv)


def _parse_command(args) -> Cmd:
    i, argc = 1, len(args)

    input_filename = None
    output_filename = None
    input_from_pastebin = False
    configure = False
    help_me = True if argc == 1 else False
    output_to_stdout = False

    while i < argc:
        temp = args[i]

        if temp in ['configure', 'conf', '--configure', '--conf', 'cfg', '--cfg', '--c']:
            configure = True

        elif temp in ['help', '--help', '-h', '--h']:
            help_me = True

        elif temp in ['-o', '--o']:
            assert i + 1 < argc, f'-o symbol without output filename, try "m2l foo.md -o foo.tex".'

            output_filename = args[i + 1]

            i += 1

        elif temp in ['-pb', '--pb', '-p', '--p', 'pastebin', '--pastebin']:
            input_from_pastebin = True

        elif temp in ['-stdout', '--stdout', '-print', '--print']:
            output_to_stdout = True

        else:
            input_filename = temp

        i += 1

    return Cmd(
        input_filename,
        output_filename,
        input_from_pastebin,
        configure,
        help_me,
        output_to_stdout
    )
