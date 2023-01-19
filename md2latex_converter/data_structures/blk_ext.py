from md2latex_converter.core.inline import texify
from md2latex_converter.data_structures.blocks import Component, BUILTIN_NAME_BLOCK_MAP, BUILTIN_PREFIX_BLOCK_MAP
from md2latex_converter.data_structures.prototypes import Sentence
from md2latex_converter.data_structures.runtime_maps import EXTENDED_PREFIX_BLOCK_MAP, EXTENDED_NAME_SENTENCE_MAP, \
    EXTENDED_NAME_BLOCK_MAP
from md2latex_converter.data_structures.sentences import BUILTIN_SENTENCES_MAP


class _Identification:
    mapped: type[Sentence]
    compositions: list[tuple[str, str, type[Sentence]]]

    def __init__(self, compositions: list[dict]):
        self.compositions = []

        for _ in compositions:
            assert isinstance(_, dict) and len(_) == 2, f'wrong identification! not a dict'
            assert 'sentence' in _, f'wrong identification! Missing sentence'
            name = _['sentence']
            assert 'occurrence' in _, f'wrong identification! Missing occurrence'
            occurrence = _['occurrence']

            assert occurrence in ['1', '*', '+'], f'occurrence should be among "1", "*", "+". Reading {occurrence}'

            if name in BUILTIN_SENTENCES_MAP:
                self.compositions.append((name, occurrence, BUILTIN_SENTENCES_MAP[name]))
            elif name in EXTENDED_NAME_SENTENCE_MAP:
                self.compositions.append((name, occurrence, EXTENDED_NAME_SENTENCE_MAP[name]))
            elif name == 'Sentence':
                self.compositions.append((name, occurrence, Sentence))
            else:
                assert False, f'Unknown sentence type {name}'

            assert self.compositions[0][2] != Sentence, f'Cannot expect "Sentence" at start of identification!'

    @property
    def prefix(self) -> type[Sentence]:
        return self.compositions[0][2]

    def parse(self, tokenizer):
        ret = []
        for name, occurrence, stype in self.compositions:
            assert occurrence in ['1', '*', '+'], f'occurrence should be among "1", "*", "+". Reading {occurrence}'

            if occurrence == '1':
                assert isinstance(tokenizer.peek, stype), f'missing {stype.identifier} in line {tokenizer.line}'
                ret.append(tokenizer.peek)
                tokenizer.next()
            elif occurrence == '*':
                temp = []
                while isinstance(tokenizer.peek, stype):
                    temp.append(tokenizer.peek)
                    tokenizer.next()
                ret.append(temp)
            elif occurrence == '+':
                temp = []
                assert isinstance(tokenizer.peek, type), f'missing {stype.identifier} in line {tokenizer.line}'
                ret.append(tokenizer.peek)
                tokenizer.next()
                while isinstance(tokenizer.peek, type):
                    temp.append(tokenizer.peek)
                    tokenizer.next()
                ret.append(temp)

        return ret


class _ToLaTeX:

    def __init__(self):
        pass

    def toLaTeX(self, located) -> str:
        pass


class _ToStr(_ToLaTeX):
    _target_str: str

    def __init__(self, target_str: str):
        super().__init__()
        self._target_str = target_str

    def toLaTeX(self, located) -> str:
        return self._target_str


class _ToLineBreak(_ToLaTeX):
    _target_str: str

    def __init__(self):
        super().__init__()
        self._target_str = '\n'

    def toLaTeX(self, located) -> str:
        return '\n'


class _ToIndent(_ToLaTeX):
    _target_str: str

    def __init__(self):
        super().__init__()
        self._target_str = '\t'

    def toLaTeX(self, located) -> str:
        return '\t'


class _ToRef(_ToLaTeX):
    to_latex: list[_ToLaTeX]
    ref_id: int

    def __init__(self, ref_id: int, to_latex: list[_ToLaTeX]):
        super().__init__()
        self.ref_id = ref_id
        self.to_latex = to_latex

    def toLaTeX(self, located) -> str:
        assert isinstance(located, list), f'wrong toLaTeX! Want to ref into not an array!'
        assert len(located) > self.ref_id
        referenced = located[self.ref_id]
        return ''.join([_.toLaTeX(referenced) for _ in self.to_latex])


class _ToForeach(_ToLaTeX):
    def __init__(self, to_latex: list[_ToLaTeX]):
        super().__init__()
        self.to_latex = to_latex

    def toLaTeX(self, located) -> str:
        assert isinstance(located, list), f'wrong toLaTeX! Want to foreach on not an array!'
        return ''.join([''.join([_.toLaTeX(_1) for _ in self.to_latex]) for _1 in located])


class _ToTexify(_ToLaTeX):
    def __init__(self):
        super().__init__()

    def toLaTeX(self, located) -> str:
        assert isinstance(located, Sentence), f'wrong toLaTeX! Want to texify a non-string! {located}'
        return texify(located.content)


def factory(commands: list) -> list[_ToLaTeX]:
    ret = []
    for command in commands:
        if isinstance(command, str):
            if command == '\n':
                ret.append(_ToLineBreak())
                continue
            elif command == '\t':
                ret.append(_ToIndent())
                continue
            else:
                ret.append(_ToStr(command))
        elif isinstance(command, dict):
            assert 'method' in command, f'wrong toLaTeX! No method specified! {command}'
            method = command['method']
            if method == 'ref':
                assert 'ref_id' in command, f'wrong toLaTeX! No ref_id specified! {command}'
                ref_id = command['ref_id']
                assert 'toLaTeX' in command, f'wrong toLaTeX! No toLaTeX specified! {command}'
                to_latex = command['toLaTeX']
                assert isinstance(to_latex, list), f'wrong toLaTeX! should be a list! {to_latex}'
                to_latex = factory(to_latex)
                ret.append(_ToRef(ref_id, to_latex))
            elif method == 'foreach':
                assert 'toLaTeX' in command, f'wrong toLaTeX! No toLaTeX specified! {command}'
                to_latex = command['toLaTeX']
                assert isinstance(to_latex, list), f'wrong toLaTeX! should be a list! {to_latex}'
                to_latex = factory(to_latex)
                ret.append(_ToForeach(to_latex))
            elif method == 'texify':
                ret.append(_ToTexify())
    return ret


class BlkExt:
    name: str
    identification: _Identification
    toLaTeX: list[_ToLaTeX]

    def __init__(self, obj: dict):
        assert 'name' in obj, f'missing name! {obj}'
        assert isinstance(obj['name'], str)
        self.name = name = obj['name']
        assert self.name not in BUILTIN_NAME_BLOCK_MAP, f'choose another name please!'
        assert self.name not in EXTENDED_NAME_BLOCK_MAP, f'choose another name please!'

        assert 'identification' in obj, f'missing identification! {obj}'
        self.identification_obj = obj['identification']
        assert isinstance(self.identification_obj, list)
        self.identification = identification = _Identification(self.identification_obj)
        assert self.identification.prefix not in BUILTIN_PREFIX_BLOCK_MAP, \
            f'duplicate prefix {self.identification.prefix.identifier}'
        assert self.identification.prefix not in EXTENDED_PREFIX_BLOCK_MAP, \
            f'duplicate prefix {self.identification.prefix.identifier}'

        assert 'toLaTeX' in obj, f'missing toLaTeX! {obj}'
        self.toLaTeX_obj = obj['toLaTeX']
        assert isinstance(self.toLaTeX_obj, list)
        self.toLaTeX = to_latex = factory(self.toLaTeX_obj)

        class ExtendedBlk(Component):
            block_name = name

            def __init__(self, parsed: list):
                self.parsed = parsed

            @staticmethod
            def parse(tokenizer):
                parsed = identification.parse(tokenizer)
                return ExtendedBlk(parsed)

            def toLaTeX(self) -> list[tuple[int, str]]:
                ret = 0, ''.join([_.toLaTeX(self.parsed) for _ in to_latex])
                return [ret]

            def __str__(self):
                return self.toLaTeX()[0]

        self.generated_blk = ExtendedBlk

        EXTENDED_NAME_BLOCK_MAP[self.name] = self.generated_blk
        EXTENDED_PREFIX_BLOCK_MAP[self.identification.prefix] = self.generated_blk
