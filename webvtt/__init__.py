"""Main webvtt package."""

__version__ = '0.5.0'

from .webvtt import WebVTT
from . import segmenter
from .models import Caption, Style  # noqa

__all__ = ['WebVTT', 'Caption', 'Style']

read = WebVTT.read
read_buffer = WebVTT.read_buffer
from_buffer = WebVTT.from_buffer
from_srt = WebVTT.from_srt
from_sbv = WebVTT.from_sbv
segment = segmenter.segment
