"""Models module."""

import re
import typing
from datetime import datetime, time

from .errors import MalformedCaptionError


class Caption:
    """Representation of a caption."""

    CUE_TEXT_TAGS = re.compile('<.*?>')

    def __init__(self,
                 start: typing.Optional[typing.Union[str, time]] = None,
                 end: typing.Optional[typing.Union[str, time]] = None,
                 text: typing.Optional[typing.Union[str,
                                                    typing.Sequence[str]
                                                    ]] = None,
                 identifier: typing.Optional[str] = None
                 ):
        """
        Initialize.

        :param start: start time of the caption
        :param end: end time of the caption
        :param text: the text of the caption
        :param identifier: optional identifier
        """
        text = text or []
        self.start = start or time()
        self.end = end or time()
        self.identifier = identifier
        self.lines = (text.splitlines()
                      if isinstance(text, str)
                      else
                      list(text)
                      )
        self.comments: typing.List[str] = []

    def __repr__(self):
        """Return the string representation of the caption."""
        cleaned_text = self.text.replace('\n', '\\n')
        return (f'<{self.__class__.__name__} '
                f'start={self.start!r} '
                f'end={self.end!r} '
                f'text={cleaned_text!r} '
                f'identifier={self.identifier!r}>'
                )

    def __str__(self):
        """Return a readable representation of the caption."""
        cleaned_text = self.text.replace('\n', '\\n')
        return f'{self.start} {self.end} {cleaned_text}'

    def __eq__(self, other):
        """Compare equality with another object."""
        if not isinstance(other, type(self)):
            return False

        return (self.start == other.start and
                self.end == other.end and
                self.raw_text == other.raw_text and
                self.identifier == other.identifier
                )

    @property
    def start(self):
        """Return the start time of the caption."""
        return self.format_timestamp(self._start)

    @start.setter
    def start(self, value: typing.Union[str, time]):
        """Set the start time of the caption."""
        self._start = self.parse_timestamp(value)

    @property
    def end(self):
        """Return the end time of the caption."""
        return self.format_timestamp(self._end)

    @end.setter
    def end(self, value: typing.Union[str, time]):
        """Set the end time of the caption."""
        self._end = self.parse_timestamp(value)

    @property
    def start_in_seconds(self) -> int:
        """Return the start time of the caption in seconds."""
        return self.time_in_seconds(self._start)

    @property
    def end_in_seconds(self):
        """Return the end time of the caption in seconds."""
        return self.time_in_seconds(self._end)

    @property
    def raw_text(self) -> str:
        """Return the text of the caption (including cue tags)."""
        return '\n'.join(self.lines)

    @property
    def text(self) -> str:
        """Return the text of the caption (without cue tags)."""
        return re.sub(self.CUE_TEXT_TAGS, '', self.raw_text)

    @text.setter
    def text(self, value: str):
        """Set the text of the captions."""
        if not isinstance(value, str):
            raise AttributeError(
                f'String value expected but received {value}.'
                )

        self.lines = value.splitlines()

    @staticmethod
    def parse_timestamp(value: typing.Union[str, time]) -> time:
        """Return timestamp as time object if in string format."""
        if isinstance(value, str):
            time_format = '%H:%M:%S.%f' if len(value) >= 11 else '%M:%S.%f'
            try:
                return datetime.strptime(value, time_format).time()
            except ValueError:
                raise MalformedCaptionError(f'Invalid timestamp: {value}')
        elif isinstance(value, time):
            return value

        raise TypeError(f'The type {type(value)} is not supported')

    @staticmethod
    def format_timestamp(time_obj: time) -> str:
        """Format timestamp in string format."""
        microseconds = int(time_obj.microsecond / 1000)
        return f'{time_obj.strftime("%H:%M:%S")}.{microseconds:03d}'

    @staticmethod
    def time_in_seconds(time_obj: time) -> int:
        """Return the time in seconds."""
        return (time_obj.hour * 3600 +
                time_obj.minute * 60 +
                time_obj.second +
                time_obj.microsecond // 1_000_000
                )


class Style:
    """Representation of a style."""

    def __init__(self, text: typing.Union[str, typing.List[str]]):
        """Initialize.

        :param: text: the style text
        """
        self.lines = text.splitlines() if isinstance(text, str) else text
        self.comments: typing.List[str] = []

    @property
    def text(self):
        """Return the text of the style."""
        return '\n'.join(self.lines)
