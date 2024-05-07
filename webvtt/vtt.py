"""VTT format module."""

import re
import typing
from .errors import MalformedFileError
from .models import Caption, Style
from . import utils


class WebVTTCueBlock:
    """Representation of a cue timing block."""

    CUE_TIMINGS_PATTERN = re.compile(
        r'\s*((?:\d+:)?\d{2}:\d{2}.\d{3})\s*-->\s*((?:\d+:)?\d{2}:\d{2}.\d{3})'
        )

    def __init__(
            self,
            identifier,
            start,
            end,
            payload
            ):
        """
        Initialize.

        :param start: start time
        :param end: end time
        :param payload: caption text
        """
        self.identifier = identifier
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
            (
              len(lines) >= 2 and
              re.match(cls.CUE_TIMINGS_PATTERN, lines[0]) and
              "-->" not in lines[1]
              ) or
            (
              len(lines) >= 3 and
              "-->" not in lines[0] and
              re.match(cls.CUE_TIMINGS_PATTERN, lines[1]) and
              "-->" not in lines[2]
              )
        )

    @classmethod
    def from_lines(
            cls,
            lines: typing.Iterable[str]
            ) -> 'WebVTTCueBlock':
        """
        Create a `WebVTTCueBlock` from lines of text.

        :param lines: the lines of text
        :returns: `WebVTTCueBlock` instance
        """
        identifier = None
        start = None
        end = None
        payload = []

        for line in lines:
            timing_match = re.match(cls.CUE_TIMINGS_PATTERN, line)
            if timing_match:
                start = timing_match.group(1)
                end = timing_match.group(2)
            elif not start:
                identifier = line
            else:
                payload.append(line)

        return cls(identifier, start, end, payload)


class WebVTTCommentBlock:
    """Representation of a comment block."""

    COMMENT_PATTERN = re.compile(r'NOTE\s(.*?)\Z', re.DOTALL)

    def __init__(self, text: str):
        """
        Initialize.

        :param text: comment text
        """
        self.text = text

    @classmethod
    def is_valid(
            cls,
            lines: typing.Sequence[str]
            ) -> bool:
        """
        Validate the lines for a match of a comment block.

        :param lines: the lines to be validated
        :returns: true for a matching comment block
        """
        return bool(lines and lines[0].startswith('NOTE'))

    @classmethod
    def from_lines(
            cls,
            lines: typing.Iterable[str]
            ) -> 'WebVTTCommentBlock':
        """
        Create a `WebVTTCommentBlock` from lines of text.

        :param lines: the lines of text
        :returns: `WebVTTCommentBlock` instance
        """
        match = cls.COMMENT_PATTERN.match('\n'.join(lines))
        return cls(text=match.group(1).strip() if match else '')


class WebVTTStyleBlock:
    """Representation of a style block."""

    STYLE_PATTERN = re.compile(r'STYLE\s(.*?)\Z', re.DOTALL)

    def __init__(self, text: str):
        """
        Initialize.

        :param text: style text
        """
        self.text = text

    @classmethod
    def is_valid(
            cls,
            lines: typing.Sequence[str]
            ) -> bool:
        """
        Validate the lines for a match of a style block.

        :param lines: the lines to be validated
        :returns: true for a matching style block
        """
        return (len(lines) >= 2 and
                lines[0] == 'STYLE' and
                not any(line.strip() == '' or '-->' in line for line in lines)
                )

    @classmethod
    def from_lines(
            cls,
            lines: typing.Iterable[str]
            ) -> 'WebVTTStyleBlock':
        """
        Create a `WebVTTStyleBlock` from lines of text.

        :param lines: the lines of text
        :returns: `WebVTTStyleBlock` instance
        """
        match = cls.STYLE_PATTERN.match('\n'.join(lines))
        return cls(text=match.group(1).strip() if match else '')


def parse(
        lines: typing.Sequence[str]
        ) -> typing.Tuple[typing.List[Caption], typing.List[Style]]:
    """
    Parse VTT captions from lines of text.

    :param lines: lines of text
    :returns: tuple of a list of `Caption` objects and a list of `Style`
    objects
    """
    if not is_valid_content(lines):
        raise MalformedFileError('Invalid format')

    items = parse_items(lines)
    return ([item for item in items if isinstance(item, Caption)],
            [item for item in items if isinstance(item, Style)]
            )


def is_valid_content(lines: typing.Sequence[str]) -> bool:
    """
    Validate lines of text for valid VTT content.

    :param lines: lines of text
    :returns: true for a valid VTT content
    """
    return bool(lines and lines[0].startswith('WEBVTT'))


def parse_items(
        lines: typing.Sequence[str]
        ) -> typing.List[typing.Union[Caption, Style]]:
    """
    Parse items from the text.

    :param lines: lines of text
    :returns: a list of `Caption` objects or `Style` objects
    """
    items: typing.List[typing.Union[Caption, Style]] = []
    comments: typing.List[WebVTTCommentBlock] = []

    for block_lines in utils.iter_blocks_of_lines(lines):
        item = parse_item(block_lines)
        if item:
            item.comments = [comment.text for comment in comments]
            comments = []
            items.append(item)
        elif WebVTTCommentBlock.is_valid(block_lines):
            comments.append(WebVTTCommentBlock.from_lines(block_lines))

    if comments and items:
        items[-1].comments.extend(
            [comment.text for comment in comments]
            )

    return items


def parse_item(
        lines: typing.Sequence[str]
        ) -> typing.Union[Caption, Style, None]:
    """
    Parse an item from lines of text.

    :param lines: lines of text
    :returns: An item (Caption or Style) if found, otherwise None
    """
    if WebVTTCueBlock.is_valid(lines):
        cue_block = WebVTTCueBlock.from_lines(lines)
        return Caption(cue_block.start,
                       cue_block.end,
                       cue_block.payload,
                       cue_block.identifier
                       )

    if WebVTTStyleBlock.is_valid(lines):
        return Style(WebVTTStyleBlock.from_lines(lines).text)

    return None


def write(
        f: typing.IO[str],
        captions: typing.Iterable[Caption]
        ):
    """
    Write captions to an output.

    :param f: file or file-like object
    :param captions: Iterable of `Caption` objects
    """
    f.write(to_str(captions))


def to_str(captions: typing.Iterable[Caption]) -> str:
    """
    Convert captions to a string with webvtt format.

    :returns: String of the captions with WebVTT format.
    """
    output = ['WEBVTT']
    for caption in captions:
        output.extend([
            '',
            *(identifier for identifier in {caption.identifier} if identifier),
            f'{caption.start} --> {caption.end}',
            *caption.lines
        ])
    return '\n'.join(output)
