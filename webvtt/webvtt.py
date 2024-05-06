"""WebVTT module."""

import os
import typing
import warnings

from . import vtt, utils
from . import srt
from . import sbv
from .models import Caption, Style
from .errors import MissingFilenameError


class WebVTT:
    """
    Parse captions in WebVTT format and also from other formats like SRT.

    To read WebVTT:

        WebVTT.read('captions.vtt')

    For other formats:

        WebVTT.from_srt('captions.srt')
        WebVTT.from_sbv('captions.sbv')
    """

    def __init__(
            self,
            file: typing.Optional[str] = None,
            captions: typing.Optional[typing.List[Caption]] = None,
            styles: typing.Optional[typing.List[Style]] = None,
            bom: bool = False
            ):
        """
        Initialize.

        :param file: the path of the WebVTT file
        :param captions: the list of captions
        :param styles: the list of styles
        :param bom: include Byte Order Mark. Default is not to include it.
        """
        self.file = file
        self.captions = captions or []
        self.styles = styles or []
        self._bom_encoding = None

    def __len__(self):
        """Return the number of captions."""
        return len(self.captions)

    def __getitem__(self, index):
        """Return a caption by index."""
        return self.captions[index]

    def __repr__(self):
        """Return the string representation of the WebVTT file."""
        return f'<{self.__class__.__name__} file={self.file}>'

    def __str__(self):
        """Return a readable representation of the WebVTT content."""
        return '\n'.join(str(c) for c in self.captions)

    @classmethod
    def read(
            cls,
            file: str,
            encoding: typing.Optional[str] = None
            ) -> 'WebVTT':
        """
        Read a WebVTT captions file.

        :param file: the file path
        :param encoding: encoding of the file
        :returns: a `WebVTT` instance
        """
        with utils.FileWrapper.open(file, encoding=encoding) as fw:
            instance = cls.from_buffer(fw.file)
            instance._bom_encoding = fw.bom_encoding
            return instance

    @classmethod
    def read_buffer(
            cls,
            buffer: typing.Iterator[str]
            ) -> 'WebVTT':
        """
        Read WebVTT captions from a file-like object.

        This method is DEPRECATED. Use from_buffer instead.

        Such file-like object may be the return of an io.open call,
        io.StringIO object, tempfile.TemporaryFile object, etc.

        :param buffer: the file-like object to read captions from
        :returns: a `WebVTT` instance
        """
        warnings.warn(
            'Deprecated: use from_buffer instead.',
            DeprecationWarning
            )
        return cls.from_buffer(buffer)

    @classmethod
    def from_buffer(
            cls,
            buffer: typing.Iterator[str]
            ) -> 'WebVTT':
        """
        Read WebVTT captions from a file-like object.

        Such file-like object may be the return of an io.open call,
        io.StringIO object, tempfile.TemporaryFile object, etc.

        :param buffer: the file-like object to read captions from
        :returns: a `WebVTT` instance
        """
        captions, styles = vtt.parse(cls._get_lines(buffer))

        return cls(
            file=getattr(buffer, 'name', None),
            captions=captions,
            styles=styles
            )

    @classmethod
    def from_srt(
            cls,
            file: str,
            encoding: typing.Optional[str] = None
            ) -> 'WebVTT':
        """
        Read captions from a file in SubRip format.

        :param file: the file path
        :param encoding: encoding of the file
        :returns: a `WebVTT` instance
        """
        with utils.FileWrapper.open(file, encoding=encoding) as fw:
            return cls(
                file=fw.file.name,
                captions=srt.parse(cls._get_lines(fw.file))
                )

    @classmethod
    def from_sbv(
            cls,
            file: str,
            encoding: typing.Optional[str] = None
            ) -> 'WebVTT':
        """
        Read captions from a file in YouTube SBV format.

        :param file: the file path
        :param encoding: encoding of the file
        :returns: a `WebVTT` instance
        """
        with utils.FileWrapper.open(file, encoding=encoding) as fw:
            return cls(
                file=fw.file.name,
                captions=sbv.parse(cls._get_lines(fw.file)),
                )

    @classmethod
    def from_string(cls, string: str) -> 'WebVTT':
        """
        Read captions from a string.

        :param string: the captions in a string
        :returns: a `WebVTT` instance
        """
        captions, styles = vtt.parse(cls._get_lines(string.splitlines()))
        return cls(
            captions=captions,
            styles=styles
            )

    @staticmethod
    def _get_lines(lines: typing.Iterable[str]) -> typing.List[str]:
        """
        Return cleaned lines from an iterable of lines.

        :param lines: iterable of lines
        :returns: a list of cleaned lines
        """
        return [line.rstrip('\n\r') for line in lines]

    def _get_destination_file(
            self,
            destination_path: typing.Optional[str] = None,
            extension: str = 'vtt'
            ) -> str:
        """
        Return the destination file based on the provided params.

        :param destination_path: optional destination path
        :param extension: the extension of the file
        :returns: the destination file

        :raises MissingFilenameError: if destination path cannot be determined
        """
        if not destination_path and not self.file:
            raise MissingFilenameError

        if not destination_path and self.file:
            destination_path = (
                f'{os.path.splitext(self.file)[0]}.{extension}'
                )

        assert destination_path is not None

        target = os.path.join(os.getcwd(), destination_path)
        if os.path.isdir(target):
            if not self.file:
                raise MissingFilenameError

            # store the file in specified directory
            base_name = os.path.splitext(os.path.basename(self.file))[0]
            new_filename = f'{base_name}.{extension}'
            return os.path.join(target, new_filename)

        if target[-4:].lower() != f'.{extension}':
            target = f'{target}.{extension}'

        # store the file in the specified full path
        return target

    def save(
            self,
            output: typing.Optional[str] = None
            ):
        """
        Save the WebVTT captions to a file.

        :param output: destination path of the file

        :raises MissingFilenameError: if output cannot be determined
        """
        destination_file = self._get_destination_file(output)
        with open(destination_file, 'w', encoding='utf-8') as f:
            vtt.write(f, self.captions)
        self.file = destination_file

    def save_as_srt(
            self,
            output: typing.Optional[str] = None
            ):
        """
        Save the WebVTT captions to a file in SubRip format.

        :param output: destination path of the file

        :raises MissingFilenameError: if output cannot be determined
        """
        dest_file = self._get_destination_file(output, extension='srt')
        with open(dest_file, 'w', encoding='utf-8') as f:
            srt.write(f, self.captions)
        self.file = dest_file

    def write(
            self,
            f: typing.IO[str],
            format: str = 'vtt'
            ):
        """
        Save the WebVTT captions to a file-like object.

        :param f: destination file-like object
        :param format: the format to use (`vtt` or `srt`)

        :raises MissingFilenameError: if output cannot be determined
        """
        if format == 'vtt':
            return vtt.write(f, self.captions)
        elif format == 'srt':
            return srt.write(f, self.captions)

        raise ValueError(f'Format {format} is not supported.')

    @property
    def total_length(self):
        """Returns the total length of the captions."""
        if not self.captions:
            return 0
        return (
                self.captions[-1].end_in_seconds -
                self.captions[0].start_in_seconds
                )

    @property
    def content(self) -> str:
        """
        Return the webvtt capions as string.

        This property is useful in cases where the webvtt content is needed
        but no file-like destination is required. Storage in DB for instance.
        """
        return vtt.to_str(self.captions)
