import os
import typing
import codecs
import warnings

from . import writers
from .parsers import WebVTTParser, SRTParser, SBVParser, Parser
from .structures import Caption, Style
from .errors import MissingFilenameError

CODEC_BOMS = {
    'utf-8-sig': codecs.BOM_UTF8,
    'utf-32-le': codecs.BOM_UTF32_LE,
    'utf-32-be': codecs.BOM_UTF32_BE,
    'utf-16-le': codecs.BOM_UTF16_LE,
    'utf-16-be': codecs.BOM_UTF16_BE
}


class WebVTT:
    """
    Parse captions in WebVTT format and also from other formats like SRT.

    To read WebVTT:

        WebVTT.read('captions.vtt')

    For other formats:

        WebVTT.from_srt('captions.srt')
        WebVTT.from_sbv('captions.sbv')
    """

    def __init__(self,
                 file: typing.Optional[str] = None,
                 captions: typing.Optional[typing.List[Caption]] = None,
                 styles: typing.Optional[typing.List[Style]] = None
                 ):
        self.file = file
        self.captions = captions or []
        self.styles = styles or []

    def __len__(self):
        return len(self.captions)

    def __getitem__(self, index):
        return self.captions[index]

    def __repr__(self):
        return f'<{self.__class__.__name__} file={self.file}>'

    def __str__(self):
        return '\n'.join(str(c) for c in self.captions)

    @classmethod
    def read(
            cls,
            file: str,
            encoding: typing.Optional[str] = None
            ) -> 'WebVTT':
        """Read a WebVTT captions file."""
        with cls._open_file(file, encoding=encoding) as f:
            return cls.from_buffer(f)

    @classmethod
    def read_buffer(cls, buffer: typing.Iterator[str]) -> 'WebVTT':
        """
        [DEPRECATED] Read WebVTT captions from a file-like object.

        Such file-like object may be the return of an io.open call,
        io.StringIO object, tempfile.TemporaryFile object, etc.
        """
        warnings.warn(
            'Deprecated: use from_buffer instead.',
            DeprecationWarning
            )
        return cls.from_buffer(buffer)

    @classmethod
    def from_buffer(cls, buffer: typing.Iterator[str]) -> 'WebVTT':
        """
        Read WebVTT captions from a file-like object.

        Such file-like object may be the return of an io.open call,
        io.StringIO object, tempfile.TemporaryFile object, etc.
        """
        items = cls._parse_content(buffer, parser=WebVTTParser)

        return cls(file=getattr(buffer, 'name', None),
                   captions=items[0],
                   styles=items[1]
                   )

    @classmethod
    def from_srt(
            cls,
            file: str,
            encoding: typing.Optional[str] = None
            ) -> 'WebVTT':
        """Read captions from a file in SubRip format."""
        with cls._open_file(file, encoding=encoding) as f:
            return cls(file=f.name,
                       captions=cls._parse_content(f, parser=SRTParser)[0],
                       )

    @classmethod
    def from_sbv(
            cls,
            file: str,
            encoding: typing.Optional[str] = None
            ) -> 'WebVTT':
        """Read captions from a file in YouTube SBV format."""
        with cls._open_file(file, encoding=encoding) as f:
            return cls(file=f.name,
                       captions=cls._parse_content(f, parser=SBVParser)[0],
                       )

    @classmethod
    def from_string(cls, string: str) -> 'WebVTT':
        return cls(
                captions=cls._parse_content(string.splitlines(),
                                            parser=WebVTTParser
                                            )[0]
                )

    @classmethod
    def _open_file(
            cls,
            file_path: str,
            encoding: typing.Optional[str] = None
            ) -> typing.IO:
        return open(
            file_path,
            encoding=encoding or cls._detect_encoding(file_path) or 'utf-8'
            )

    @classmethod
    def _parse_content(
            cls,
            content: typing.Iterable[str],
            parser: typing.Type[Parser]
            ) -> typing.Tuple[typing.List[Caption], typing.List[Style]]:
        lines = [line.rstrip('\n\r') for line in content]
        items = parser.parse(lines)
        return (list(filter(lambda c: isinstance(c, Caption), items)),
                list(filter(lambda s: isinstance(s, Style), items))
                )

    @staticmethod
    def _detect_encoding(file_path: str) -> typing.Optional[str]:
        with open(file_path, mode='rb') as f:
            first_bytes = f.read(4)
            for encoding, bom in CODEC_BOMS.items():
                if first_bytes.startswith(bom):
                    return encoding
        return None

    def _get_destination_file(
            self,
            destination_path: typing.Optional[str] = None,
            extension: str = 'vtt'
            ):
        if not destination_path and not self.file:
            raise MissingFilenameError

        assert self.file is not None

        destination_path = (
                destination_path or
                f'{os.path.splitext(self.file)[0]}.{extension}'
                )

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

    def save(self, output: typing.Optional[str] = None):
        """
        Save the WebVTT captions to a file.

        If no output is provided the file will be saved in the same location.
        Otherwise output can determine a target directory or file.
        """
        destination_file = self._get_destination_file(output)
        with open(destination_file, 'w', encoding='utf-8') as f:
            self.write(f)
        self.file = destination_file

    def save_as_srt(self, output: typing.Optional[str] = None):
        dest_file = self._get_destination_file(output, extension='srt')
        with open(dest_file, 'w', encoding='utf-8') as f:
            self.write(f, format='srt')
        self.file = dest_file

    def write(self, f: typing.IO[str], format: str = 'vtt'):
        if format == 'vtt':
            writers.write_vtt(f, self.captions)
        elif format == 'srt':
            writers.write_srt(f, self.captions)
        else:
            raise ValueError(f'Format {format!r} is not supported')

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
        but no file saving on the system is required.
        """
        return writers.webvtt_content(self.captions)
