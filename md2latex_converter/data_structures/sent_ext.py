import re

from md2latex_converter.data_structures.prototypes import Sentence
from md2latex_converter.data_structures.runtime_maps import EXTENDED_NAME_SENTENCE_MAP, EXTENDED_REGEX_SENTENCE_MAP
from md2latex_converter.data_structures.sentences import BUILTIN_SENTENCES


class SentExt:
    """
    sentence extension, to allow DIY sentence types.

        'identifier' is the extended sentence identifier;

        'regex' to identify and declare parts to be recorded;

    ----

    The SentExt.__init__(self, name, regex) method returns an instance of SentExt

        The instance itself contains another class as generated_type

        - The generated_type is a subclass of prototypes.Sentence
        - The generated_type.__init__(index, content) is generated during runtime to do the identifying and recording

    ----

    to rename a part: use 'foo(?P<barrrr>bar*)'

    to declare that this regex will capture 'bar*' occurrences and record them with name 'barrrr'

    ----

    If regex matches, construction method will be invoked.

    The parts to be recorded in the sentence will be recorded into recorded_dict

    ----

    The init method is invoked on every sentence extension, each time building a SentExt instance, with name
    `identifier` and sentence type `generated_type`

    The call of SentExt('FOO', r'```(?P<lang>.*)') **on** runtime is equal to declare as follows **before** runtime:

        class FOO(Sentence):
            def __init__(self, line, content):
                match = re.match(r'```(?P<lang>.*)')

                super().__init__(line, 'FOO', content)

                self.recorded_dict = dict()

                self.recorded_dict['lang'] = match.groupdict()['lang']
    """

    identifier: str
    regex: str
    generated_type: type

    def __init__(self, name: str, regex: str):
        assert name not in BUILTIN_SENTENCES, f'Name {name} is already used!'
        assert name not in EXTENDED_NAME_SENTENCE_MAP, f'Name {name} is already used!'

        self.identifier = name
        self.regex = regex
        self.pattern = re.compile(regex)
        self.recorded_names = list(self.pattern.groupindex.keys())

        class SentExtInstance(Sentence):
            recoded_dict: dict[str, str]
            _name = name
            _recoded_names = self.recorded_names

            def __init__(self, line, content):
                assert (match := re.match(regex, content)) is not None, f'Extended sentence does not match! {name}'
                super().__init__(line, name, content)
                self.recoded_dict = match.groupdict()

        self.generated_type = SentExtInstance

        EXTENDED_NAME_SENTENCE_MAP[name] = SentExtInstance
        EXTENDED_REGEX_SENTENCE_MAP[regex] = SentExtInstance

    def __str__(self):
        return f'{self.identifier}: <{self.regex}>'
