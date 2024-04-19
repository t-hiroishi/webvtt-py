import typing

from .structures import Caption


class WebVTTWriter:

    def write(self, captions: typing.Iterable[Caption], f: typing.IO[str]):
        f.write(self.webvtt_content(captions))

    def webvtt_content(self, captions: typing.Iterable[Caption]) -> str:
        """
        Return captions content with webvtt formatting.
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


class SRTWriter:

    def write(self, captions, f: typing.IO[str]):
        output = []
        for index, caption in enumerate(captions, start=1):
            output.extend([
                f'{index}',
                '{} --> {}'.format(*map(lambda x: x.replace('.', ','), (caption.start, caption.end))),
                *caption.lines,
                ''
                ])
        f.write('\n'.join(output).rstrip())


class SBVWriter(object):
    pass
