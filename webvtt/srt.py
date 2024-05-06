"""SRT format module."""

import typing
import re
from datetime import datetime, time

from .models import Caption
from .errors import MalformedFileError
from . import utils


class SRTCueBlock:
    """Representation of a cue timing block."""

    CUE_TIMINGS_PATTERN = re.compile(
        r'\s*(\d+:\d{2}:\d{2},\d{3})\s*-->\s*(\d+:\d{2}:\d{2},\d{3})'
        )

    def __init__(
            self,
            index: str,
            start: time,
            end: time,
            payload: typing.Sequence[str]
            ):
        """
        Initialize.

        :param start: start time
        :param end: end time
        :param payload: caption text
        """
        self.index = index
        self.start = start
        self.end = end
        self.payload = payload

    @classmethod
    def is_valid(
            cls,
            lines: typing.Sequence[str]
            ) -> bool:
        """
        Validate the lines for a match of a cue time block.

        :param lines: the lines to be validated
        :returns: true for a matching cue time block
        """
        return bool(
          len(lines) >= 3 and
          lines[0].isdigit() and
          re.match(cls.CUE_TIMINGS_PATTERN, lines[1])
          )

    @classmethod
    def from_lines(
            cls,
            lines: typing.Sequence[str]
            ) -> 'SRTCueBlock':
        """
        Create a `SRTCueBlock` from lines of text.

        :param lines: the lines of text
        :returns: `SRTCueBlock` instance
        """
        index = lines[0]

        match = re.match(cls.CUE_TIMINGS_PATTERN, lines[1])
        assert match is not None
        start, end = map(lambda x: datetime.strptime(x, '%H:%M:%S,%f').time(),
                         (match.group(1), match.group(2))
                         )

        payload = lines[2:]

        return cls(index, start, end, payload)


def parse(lines: typing.Sequence[str]) -> typing.List[Caption]:
    """
    Parse SRT captions from lines of text.

    :param lines: lines of text
    :returns: list of `Caption` objects
    """
    if not is_valid_content(lines):
        raise MalformedFileError('Invalid format')

    return parse_captions(lines)


def is_valid_content(lines: typing.Sequence[str]) -> bool:
    """
    Validate lines of text for valid SBV content.

    :param lines: lines of text
    :returns: true for a valid SBV content
    """
    return bool(
        len(lines) >= 3 and
        lines[0].isdigit() and
        '-->' in lines[1] and
        lines[2].strip()
    )


def parse_captions(lines: typing.Sequence[str]) -> typing.List[Caption]:
    """
    Parse captions from the text.

    :param lines: lines of text
    :returns: list of `Caption` objects
    """
    captions: typing.List[Caption] = []

    for block_lines in utils.iter_blocks_of_lines(lines):
        if not SRTCueBlock.is_valid(block_lines):
            continue

        cue_block = SRTCueBlock.from_lines(block_lines)
        captions.append(Caption(cue_block.start,
                                cue_block.end,
                                cue_block.payload
                                ))

    return captions


def write(
        f: typing.IO[str],
        captions: typing.Iterable[Caption]
        ):
    """
    Write captions to an output.

    :param f: file or file-like object
    :param captions: Iterable of `Caption` objects
    """
    output = []
    for index, caption in enumerate(captions, start=1):
        output.extend([
            f'{index}',
            '{} --> {}'.format(*map(lambda x: x.replace('.', ','),
                                    (caption.start, caption.end))
                               ),
            *caption.lines,
            ''
            ])
    f.write('\n'.join(output).rstrip())
