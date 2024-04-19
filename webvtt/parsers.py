import os
import codecs
import typing
from abc import ABC, abstractmethod

from .errors import MalformedFileError
from .structures import (Style,
                         Caption,
                         WebVTTCueBlock,
                         WebVTTCommentBlock,
                         WebVTTStyleBlock,
                         SRTCueBlock,
                         SBVCueBlock,
                         )


class BaseParser(ABC):
    @classmethod
    def read(cls, file):
        """Reads the captions file."""
        return cls._parse(cls._get_content_from_file(file_path=file))

    @classmethod
    def read_from_buffer(cls, buffer):
        return cls._parse(cls._read_content_lines(buffer))

    @classmethod
    def _parse(cls, content):
        if not cls.validate(content):
            raise MalformedFileError('Invalid format')
        return cls.parse(content)

    @classmethod
    def _get_content_from_file(cls, file_path):
        encoding = cls._read_file_encoding(file_path)
        with open(file_path, encoding=encoding) as f:
            return cls._read_content_lines(f)

    @staticmethod
    def _read_file_encoding(file_path):
        first_bytes = min(32, os.path.getsize(file_path))
        with open(file_path, 'rb') as f:
            raw = f.read(first_bytes)

        if raw.startswith(codecs.BOM_UTF8):
            return 'utf-8-sig'
        else:
            return 'utf-8'

    @staticmethod
    def _read_content_lines(file_obj: typing.IO[str]):

        lines = [line.rstrip('\n\r') for line in file_obj.readlines()]

        if not lines:
            raise MalformedFileError('The file is empty.')

        return lines

    @staticmethod
    def iter_blocks_of_lines(lines) -> typing.Generator[typing.List[str], None, None]:
        current_text_block = []

        for line in lines:
            if line.strip():
                current_text_block.append(line)
            elif current_text_block:
                yield current_text_block
                current_text_block = []

        if current_text_block:
            yield current_text_block

    @classmethod
    @abstractmethod
    def validate(cls, lines: typing.Sequence[str]) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def parse(cls, lines: typing.Sequence[str]):
        raise NotImplementedError


class WebVTTParser(BaseParser):
    """
    Web Video Text Track parser.
    """

    @classmethod
    def validate(cls, lines: typing.Sequence[str]) -> bool:
        return lines[0].startswith('WEBVTT')

    @classmethod
    def parse(cls, lines: typing.Sequence[str]) -> typing.List[typing.Union[Style, Caption]]:
        items = []
        comments = []

        for block_lines in cls.iter_blocks_of_lines(lines):
            if WebVTTCueBlock.is_valid(block_lines):
                cue_block = WebVTTCueBlock.from_lines(block_lines)
                caption = Caption(cue_block.start,
                                  cue_block.end,
                                  cue_block.payload,
                                  cue_block.identifier
                                  )

                if comments:
                    caption.comments = [comment.text for comment in comments]
                    comments = []
                items.append(caption)

            elif WebVTTCommentBlock.is_valid(block_lines):
                comments.append(WebVTTCommentBlock.from_lines(block_lines))

            elif WebVTTStyleBlock.is_valid(block_lines):
                style = Style(text=WebVTTStyleBlock.from_lines(block_lines).text)
                if comments:
                    style.comments = [comment.text for comment in comments]
                    comments = []
                items.append(style)

        if comments and items:
            items[-1].comments = [comment.text for comment in comments]

        return items


class SRTParser(BaseParser):
    """
    SubRip SRT parser.
    """

    @classmethod
    def validate(cls, lines: typing.Sequence[str]) -> bool:
        return len(lines) >= 3 and lines[0].isdigit() and '-->' in lines[1] and lines[2].strip()

    @classmethod
    def parse(cls, lines: typing.Sequence[str]) -> typing.List[Caption]:
        captions = []

        for block_lines in cls.iter_blocks_of_lines(lines):
            if not SRTCueBlock.is_valid(block_lines):
                continue

            cue_block = SRTCueBlock.from_lines(block_lines)
            captions.append(Caption(cue_block.start,
                                    cue_block.end,
                                    cue_block.payload
                                    ))

        return captions


class SBVParser(BaseParser):
    """
    YouTube SBV parser.
    """

    @classmethod
    def validate(cls, lines: typing.Sequence[str]) -> bool:
        if len(lines) < 2:
            return False

        first_block = next(cls.iter_blocks_of_lines(lines))
        return first_block and SBVCueBlock.is_valid(first_block)

    @classmethod
    def parse(cls, lines: typing.Sequence[str]) -> typing.List[Caption]:
        captions = []

        for block_lines in cls.iter_blocks_of_lines(lines):
            if not SBVCueBlock.is_valid(block_lines):
                continue

            cue_block = SBVCueBlock.from_lines(block_lines)
            captions.append(Caption(cue_block.start,
                                    cue_block.end,
                                    cue_block.payload
                                    ))

        return captions
