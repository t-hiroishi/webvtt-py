import unittest
import os
import io
import textwrap
import warnings
import tempfile
import pathlib

import webvtt
from webvtt.models import Caption, Style
from webvtt.utils import CODEC_BOMS
from webvtt.errors import MalformedFileError

PATH_TO_SAMPLES = pathlib.Path(__file__).resolve().parent / 'samples'


class TestWebVTT(unittest.TestCase):

    def test_from_string(self):
        vtt = webvtt.WebVTT.from_string(textwrap.dedent("""
            WEBVTT

            00:00:00.500 --> 00:00:07.000
            Caption text #1

            00:00:07.000 --> 00:00:11.890
            Caption text #2 line 1
            Caption text #2 line 2

            00:00:11.890 --> 00:00:16.320
            Caption text #3

            00:00:16.320 --> 00:00:21.580
            Caption text #4
            """).strip())
        self.assertEqual(len(vtt), 4)
        self.assertEqual(
            str(vtt[0]),
            '00:00:00.500 00:00:07.000 Caption text #1'
            )
        self.assertEqual(
            str(vtt[1]),
            r'00:00:07.000 00:00:11.890 Caption text #2 line 1\n'
            'Caption text #2 line 2'
            )
        self.assertEqual(
            str(vtt[2]),
            '00:00:11.890 00:00:16.320 Caption text #3'
            )
        self.assertEqual(
            str(vtt[3]),
            '00:00:16.320 00:00:21.580 Caption text #4'
            )

    def test_write_captions(self):
        out = io.StringIO()
        vtt = webvtt.read(PATH_TO_SAMPLES / 'one_caption.vtt')
        new_caption = Caption(start='00:00:07.000',
                              end='00:00:11.890',
                              text=['New caption text line1',
                                    'New caption text line2'
                                    ]
                              )
        vtt.captions.append(new_caption)
        vtt.write(out)

        out.seek(0)

        self.assertEqual(
            out.read(),
            textwrap.dedent('''
                WEBVTT

                00:00:00.500 --> 00:00:07.000
                Caption text #1

                00:00:07.000 --> 00:00:11.890
                New caption text line1
                New caption text line2
            ''').strip()
            )

    def test_write_captions_in_srt(self):
        out = io.StringIO()
        vtt = webvtt.read(PATH_TO_SAMPLES / 'one_caption.vtt')
        new_caption = Caption(start='00:00:07.000',
                              end='00:00:11.890',
                              text=['New caption text line1',
                                    'New caption text line2'
                                    ]
                              )
        vtt.captions.append(new_caption)
        vtt.write(out, format='srt')

        out.seek(0)
        self.assertEqual(
            out.read(),
            textwrap.dedent('''
                1
                00:00:00,500 --> 00:00:07,000
                Caption text #1

                2
                00:00:07,000 --> 00:00:11,890
                New caption text line1
                New caption text line2
            ''').strip()
            )

    def test_write_captions_in_unsupported_format(self):
        self.assertRaises(
            ValueError,
            webvtt.WebVTT().write,
            io.StringIO(),
            format='ttt'
        )

    def test_save_captions(self):
        with tempfile.NamedTemporaryFile('w', suffix='.vtt') as f:
            f.write((PATH_TO_SAMPLES / 'one_caption.vtt').read_text())
            f.flush()

            vtt = webvtt.read(f.name)
            new_caption = Caption(start='00:00:07.000',
                                  end='00:00:11.890',
                                  text=['New caption text line1',
                                        'New caption text line2'
                                        ]
                                  )
            vtt.captions.append(new_caption)
            vtt.save()
            f.flush()

            self.assertEqual(
                pathlib.Path(f.name).read_text(),
                textwrap.dedent('''
                    WEBVTT

                    00:00:00.500 --> 00:00:07.000
                    Caption text #1

                    00:00:07.000 --> 00:00:11.890
                    New caption text line1
                    New caption text line2
                    ''').strip()
            )

    def test_srt_conversion(self):
        with tempfile.TemporaryDirectory() as td:
            with open(pathlib.Path(td) / 'one_caption.srt', 'w') as f:
                f.write((PATH_TO_SAMPLES / 'one_caption.srt').read_text())

            webvtt.from_srt(
                pathlib.Path(td) / 'one_caption.srt'
                ).save()

            self.assertTrue(
                os.path.exists(pathlib.Path(td) / 'one_caption.vtt')
                )
            self.assertEqual(
                (pathlib.Path(td) / 'one_caption.vtt').read_text(),
                textwrap.dedent('''
                    WEBVTT

                    00:00:00.500 --> 00:00:07.000
                    Caption text #1
                    ''').strip()
                )

    def test_sbv_conversion(self):
        with tempfile.TemporaryDirectory() as td:
            with open(pathlib.Path(td) / 'two_captions.sbv', 'w') as f:
                f.write(
                    (PATH_TO_SAMPLES / 'two_captions.sbv').read_text()
                    )

            webvtt.from_sbv(
                pathlib.Path(td) / 'two_captions.sbv'
                ).save()

            self.assertTrue(
                os.path.exists(pathlib.Path(td) / 'two_captions.vtt')
                )
            self.assertEqual(
                (pathlib.Path(td) / 'two_captions.vtt').read_text(),
                textwrap.dedent('''
                    WEBVTT

                    00:00:00.378 --> 00:00:11.378
                    Caption text #1

                    00:00:11.378 --> 00:00:12.305
                    Caption text #2 (line 1)
                    Caption text #2 (line 2)
                    ''').strip()
                )

    def test_save_to_other_location(self):
        with tempfile.TemporaryDirectory() as td:
            webvtt.read(
                PATH_TO_SAMPLES / 'one_caption.vtt'
                ).save(td)

            self.assertTrue(
                os.path.exists(pathlib.Path(td) / 'one_caption.vtt')
                )

    def test_save_specific_filename(self):
        with tempfile.TemporaryDirectory() as td:
            webvtt.read(
                PATH_TO_SAMPLES / 'one_caption.vtt'
                ).save(
                    pathlib.Path(td) / 'one_caption_new.vtt'
                )

            self.assertTrue(
                os.path.exists(pathlib.Path(td) / 'one_caption_new.vtt')
                )

    def test_save_specific_filename_no_extension(self):
        with tempfile.TemporaryDirectory() as td:
            webvtt.read(
                PATH_TO_SAMPLES / 'one_caption.vtt'
                ).save(
                    pathlib.Path(td) / 'one_caption_new'
                )

            self.assertTrue(
                os.path.exists(pathlib.Path(td) / 'one_caption_new.vtt')
                )

    def test_from_buffer(self):
        with open(PATH_TO_SAMPLES / 'sample.vtt', 'r', encoding='utf-8') as f:
            self.assertIsInstance(
                webvtt.from_buffer(f).captions,
                list
                )

    def test_deprecated_read_buffer(self):
        with open(PATH_TO_SAMPLES / 'sample.vtt', 'r', encoding='utf-8') as f:
            with warnings.catch_warnings(record=True) as warns:
                warnings.simplefilter('always')
                vtt = webvtt.read_buffer(f)

                self.assertIsInstance(vtt.captions, list)
                self.assertEqual(
                    'Deprecated: use from_buffer instead.',
                    str(warns[-1].message)
                    )

    def test_read_memory_buffer(self):
        buffer = io.StringIO(
            (PATH_TO_SAMPLES / 'sample.vtt').read_text()
            )

        self.assertIsInstance(
            webvtt.from_buffer(buffer).captions,
            list
            )

    def test_read_memory_buffer_carriage_return(self):
        """https://github.com/glut23/webvtt-py/issues/29"""
        buffer = io.StringIO(textwrap.dedent('''\
            WEBVTT\r
            \r
            00:00:00.500 --> 00:00:07.000\r
            Caption text #1\r
            \r
            00:00:07.000 --> 00:00:11.890\r
            Caption text #2\r
            \r
            00:00:11.890 --> 00:00:16.320\r
            Caption text #3\r
        '''))

        self.assertEqual(
            len(webvtt.from_buffer(buffer).captions),
            3
            )

    def test_read_malformed_buffer(self):
        malformed_payloads = ['', 'MOCK MALFORMED CONTENT']
        for payload in malformed_payloads:
            buffer = io.StringIO(payload)
            with self.assertRaises(MalformedFileError):
                webvtt.from_buffer(buffer)

    def test_captions(self):
        captions = webvtt.read(PATH_TO_SAMPLES / 'sample.vtt').captions
        self.assertIsInstance(
            captions,
            list
            )
        self.assertEqual(len(captions), 16)

    def test_sequence_iteration(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'sample.vtt')
        self.assertIsInstance(vtt[0], Caption)
        self.assertEqual(len(vtt), len(vtt.captions))

    def test_save_no_filename(self):
        self.assertRaises(
            webvtt.errors.MissingFilenameError,
            webvtt.WebVTT().save
        )

    def test_save_with_path_to_dir_no_filename(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertRaises(
                webvtt.errors.MissingFilenameError,
                webvtt.WebVTT().save,
                td
            )

    def test_set_styles_from_text(self):
        style = Style('::cue(b) {\n  color: peachpuff;\n}')
        self.assertListEqual(
            style.lines,
            ['::cue(b) {', '  color: peachpuff;', '}']
        )

    def test_save_identifiers(self):
        with tempfile.NamedTemporaryFile('w', suffix='.vtt') as f:
            webvtt.read(
                PATH_TO_SAMPLES / 'using_identifiers.vtt'
                ).save(
                    f.name
                    )

            self.assertListEqual(
                pathlib.Path(f.name).read_text().splitlines(),
                [
                    'WEBVTT',
                    '',
                    '00:00:00.500 --> 00:00:07.000',
                    'Caption text #1',
                    '',
                    'second caption',
                    '00:00:07.000 --> 00:00:11.890',
                    'Caption text #2',
                    '',
                    '00:00:11.890 --> 00:00:16.320',
                    'Caption text #3',
                    '',
                    '4',
                    '00:00:16.320 --> 00:00:21.580',
                    'Caption text #4',
                    '',
                    '00:00:21.580 --> 00:00:23.880',
                    'Caption text #5',
                    '',
                    '00:00:23.880 --> 00:00:27.280',
                    'Caption text #6'
                    ]
                )

    def test_save_updated_identifiers(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'using_identifiers.vtt')
        vtt.captions[0].identifier = 'first caption'
        vtt.captions[1].identifier = None
        vtt.captions[3].identifier = '44'
        last_caption = Caption(start='00:00:27.280',
                               end='00:00:29.200',
                               text='Caption text #7'
                               )
        last_caption.identifier = 'last caption'
        vtt.captions.append(last_caption)

        with tempfile.NamedTemporaryFile('w', suffix='.vtt') as f:
            vtt.save(f.name)

            self.assertListEqual(
                pathlib.Path(f.name).read_text().splitlines(),
                [
                    'WEBVTT',
                    '',
                    'first caption',
                    '00:00:00.500 --> 00:00:07.000',
                    'Caption text #1',
                    '',
                    '00:00:07.000 --> 00:00:11.890',
                    'Caption text #2',
                    '',
                    '00:00:11.890 --> 00:00:16.320',
                    'Caption text #3',
                    '',
                    '44',
                    '00:00:16.320 --> 00:00:21.580',
                    'Caption text #4',
                    '',
                    '00:00:21.580 --> 00:00:23.880',
                    'Caption text #5',
                    '',
                    '00:00:23.880 --> 00:00:27.280',
                    'Caption text #6',
                    '',
                    'last caption',
                    '00:00:27.280 --> 00:00:29.200',
                    'Caption text #7'
                ]
            )

    def test_content_formatting(self):
        """
        Verify that content property returns the correctly formatted webvtt.
        """
        captions = [
            Caption(start='00:00:00.500',
                    end='00:00:07.000',
                    text=['Caption test line 1', 'Caption test line 2']
                    ),
            Caption(start='00:00:08.000',
                    end='00:00:15.000',
                    text=['Caption test line 3', 'Caption test line 4']
                    ),
            ]

        self.assertEqual(
            webvtt.WebVTT(captions=captions).content,
            textwrap.dedent("""
                    WEBVTT

                    00:00:00.500 --> 00:00:07.000
                    Caption test line 1
                    Caption test line 2

                    00:00:08.000 --> 00:00:15.000
                    Caption test line 3
                    Caption test line 4
                    """).strip()
            )

    def test_repr(self):
        test_file = PATH_TO_SAMPLES / 'sample.vtt'
        self.assertEqual(
            repr(webvtt.read(test_file)),
            f"<WebVTT file='{test_file}' encoding='utf-8'>"
        )

    def test_str(self):
        self.assertEqual(
            str(webvtt.read(PATH_TO_SAMPLES / 'sample.vtt')),
            textwrap.dedent("""
                00:00:00.500 00:00:07.000 Caption text #1
                00:00:07.000 00:00:11.890 Caption text #2
                00:00:11.890 00:00:16.320 Caption text #3
                00:00:16.320 00:00:21.580 Caption text #4
                00:00:21.580 00:00:23.880 Caption text #5
                00:00:23.880 00:00:27.280 Caption text #6
                00:00:27.280 00:00:30.280 Caption text #7
                00:00:30.280 00:00:36.510 Caption text #8
                00:00:36.510 00:00:38.870 Caption text #9
                00:00:38.870 00:00:45.000 Caption text #10
                00:00:45.000 00:00:47.000 Caption text #11
                00:00:47.000 00:00:50.970 Caption text #12
                00:00:50.970 00:00:54.440 Caption text #13
                00:00:54.440 00:00:58.600 Caption text #14
                00:00:58.600 00:01:01.350 Caption text #15
                00:01:01.350 00:01:04.300 Caption text #16
            """).strip()
        )

    def test_parse_invalid_file(self):
        self.assertRaises(
            MalformedFileError,
            webvtt.read,
            PATH_TO_SAMPLES / 'invalid.vtt'
        )

    def test_file_not_found(self):
        self.assertRaises(
            FileNotFoundError,
            webvtt.read,
            'nowhere'
        )

    def test_total_length(self):
        self.assertEqual(
            webvtt.read(PATH_TO_SAMPLES / 'sample.vtt').total_length,
            64
        )

    def test_total_length_no_captions(self):
        self.assertEqual(
            webvtt.WebVTT().total_length,
            0
        )

    def test_parse_empty_file(self):
        self.assertRaises(
            MalformedFileError,
            webvtt.read,
            PATH_TO_SAMPLES / 'empty.vtt'
            )

    def test_parse_invalid_timeframe_line(self):
        good_captions = len(
            webvtt.read(PATH_TO_SAMPLES / 'invalid_timeframe.vtt').captions
            )
        self.assertEqual(good_captions, 6)

    def test_parse_invalid_timeframe_in_cue_text(self):
        vtt = webvtt.read(
            PATH_TO_SAMPLES / 'invalid_timeframe_in_cue_text.vtt'
            )
        self.assertEqual(2, len(vtt.captions))
        self.assertEqual('Caption text #3', vtt.captions[1].text)

    def test_parse_get_caption_data(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'one_caption.vtt')
        self.assertEqual(vtt.captions[0].start_in_seconds, 0)
        self.assertEqual(vtt.captions[0].start, '00:00:00.500')
        self.assertEqual(vtt.captions[0].end_in_seconds, 7)
        self.assertEqual(vtt.captions[0].end, '00:00:07.000')
        self.assertEqual(vtt.captions[0].lines[0], 'Caption text #1')
        self.assertEqual(len(vtt.captions[0].lines), 1)

    def test_caption_without_timeframe(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'missing_timeframe.vtt')
        self.assertEqual(len(vtt.captions), 6)

    def test_caption_without_cue_text(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'missing_caption_text.vtt')
        self.assertEqual(len(vtt.captions), 4)

    def test_timestamps_format(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'sample.vtt')
        self.assertEqual(vtt.captions[2].start, '00:00:11.890')
        self.assertEqual(vtt.captions[2].end, '00:00:16.320')

    def test_parse_timestamp(self):
        self.assertEqual(
            Caption(start='02:03:11.890').start_in_seconds,
            7391
        )

    def test_captions_attribute(self):
        self.assertListEqual(webvtt.WebVTT().captions, [])

    def test_metadata_headers(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'metadata_headers.vtt')
        self.assertEqual(len(vtt.captions), 2)

    def test_metadata_headers_multiline(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'metadata_headers_multiline.vtt')
        self.assertEqual(len(vtt.captions), 2)

    def test_parse_identifiers(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'using_identifiers.vtt')
        self.assertEqual(len(vtt.captions), 6)

        self.assertEqual(vtt.captions[1].identifier, 'second caption')
        self.assertEqual(vtt.captions[2].identifier, None)
        self.assertEqual(vtt.captions[3].identifier, '4')

    def test_parse_comments(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'comments.vtt')
        self.assertEqual(len(vtt.captions), 3)
        self.assertListEqual(
            vtt.captions[0].lines,
            ['- Ta en kopp varmt te.',
             '- Det är inte varmt.']
        )
        self.assertListEqual(
            vtt.captions[0].comments,
            ['This translation was done by Kyle so that\n'
             'some friends can watch it with their parents.'
             ]
        )
        self.assertListEqual(
            vtt.captions[1].comments,
            []
        )
        self.assertEqual(
            vtt.captions[2].text,
            '- Ta en kopp'
        )
        self.assertListEqual(
            vtt.captions[2].comments,
            ['This last line may not translate well.']
        )

    def test_parse_styles(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'styles.vtt')
        self.assertEqual(len(vtt.captions), 1)
        self.assertEqual(
            vtt.styles[0].text,
            '::cue {\n  background-image: linear-gradient(to bottom, '
            'dimgray, lightgray);\n  color: papayawhip;\n}'
        )

    def test_parse_styles_with_comments(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'styles_with_comments.vtt')
        self.assertEqual(len(vtt.captions), 1)
        self.assertEqual(len(vtt.styles), 2)
        self.assertEqual(
            vtt.styles[0].comments,
            ['This is the first style block']
            )
        self.assertEqual(
            vtt.styles[0].text,
            '::cue {\n'
            '  background-image: linear-gradient(to bottom, dimgray, '
            'lightgray);\n'
            '  color: papayawhip;\n'
            '}'
            )
        self.assertEqual(
            vtt.styles[1].comments,
            ['This is the second block of styles',
             'Multiline comment for the same\nsecond block of styles'
             ]
            )
        self.assertEqual(
            vtt.styles[1].text,
            '::cue(b) {\n'
            '  color: peachpuff;\n'
            '}'
        )

    def test_clean_cue_tags(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'cue_tags.vtt')
        self.assertEqual(
            vtt.captions[1].text,
            'Like a big-a pizza pie'
        )
        self.assertEqual(
            vtt.captions[2].text,
            'That\'s amore'
        )

    def test_parse_captions_with_bom(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'captions_with_bom.vtt')
        self.assertEqual(len(vtt.captions), 4)

    def test_empty_lines_are_not_included_in_result(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'netflix_chicas_del_cable.vtt')
        self.assertEqual(vtt.captions[0].text, "[Alba] En 1928,")
        self.assertEqual(
            vtt.captions[-2].text,
            "Diez años no son suficientes\npara olvidarte..."
        )

    def test_can_parse_youtube_dl_files(self):
        vtt = webvtt.read(PATH_TO_SAMPLES / 'youtube_dl.vtt')
        self.assertEqual(
            "this will happen is I'm telling\n ",
            vtt.captions[2].text
        )


class TestParseSRT(unittest.TestCase):

    def test_parse_empty_file(self):
        self.assertRaises(
            webvtt.errors.MalformedFileError,
            webvtt.from_srt,
            # We reuse this file as it is empty and serves the purpose.
            PATH_TO_SAMPLES / 'empty.vtt'
        )

    def test_invalid_format(self):
        for i in range(1, 5):
            self.assertRaises(
                MalformedFileError,
                webvtt.from_srt,
                PATH_TO_SAMPLES / f'invalid_format{i}.srt'
            )

    def test_total_length(self):
        self.assertEqual(
            webvtt.from_srt(PATH_TO_SAMPLES / 'sample.srt').total_length,
            23
        )

    def test_parse_captions(self):
        self.assertTrue(
            webvtt.from_srt(PATH_TO_SAMPLES / 'sample.srt').captions
            )

    def test_missing_timeframe_line(self):
        self.assertEqual(
            len(webvtt.from_srt(
                PATH_TO_SAMPLES / 'missing_timeframe.srt').captions
                ),
            4
            )

    def test_empty_caption_text(self):
        self.assertTrue(
            webvtt.from_srt(
                PATH_TO_SAMPLES / 'missing_caption_text.srt').captions
            )

    def test_empty_gets_removed(self):
        captions = webvtt.from_srt(
            PATH_TO_SAMPLES / 'missing_caption_text.srt'
            ).captions
        self.assertEqual(len(captions), 4)

    def test_invalid_timestamp(self):
        self.assertEqual(
            len(webvtt.from_srt(
                PATH_TO_SAMPLES / 'invalid_timeframe.srt'
                ).captions),
            4
            )

    def test_timestamps_format(self):
        vtt = webvtt.from_srt(PATH_TO_SAMPLES / 'sample.srt')
        self.assertEqual(vtt.captions[2].start, '00:00:11.890')
        self.assertEqual(vtt.captions[2].end, '00:00:16.320')

    def test_parse_get_caption_data(self):
        vtt = webvtt.from_srt(PATH_TO_SAMPLES / 'one_caption.srt')
        self.assertEqual(vtt.captions[0].start_in_seconds, 0)
        self.assertEqual(vtt.captions[0].start, '00:00:00.500')
        self.assertEqual(vtt.captions[0].end_in_seconds, 7)
        self.assertEqual(vtt.captions[0].end, '00:00:07.000')
        self.assertEqual(vtt.captions[0].lines[0], 'Caption text #1')
        self.assertEqual(len(vtt.captions[0].lines), 1)


class TestParseSBV(unittest.TestCase):

    def test_parse_empty_file(self):
        self.assertRaises(
            MalformedFileError,
            webvtt.from_sbv,
            # We reuse this file as it is empty and serves the purpose.
            PATH_TO_SAMPLES / 'empty.vtt'
        )

    def test_invalid_format(self):
        self.assertRaises(
            MalformedFileError,
            webvtt.from_sbv,
            PATH_TO_SAMPLES / 'invalid_format.sbv'
        )

    def test_total_length(self):
        self.assertEqual(
            webvtt.from_sbv(PATH_TO_SAMPLES / 'sample.sbv').total_length,
            16
        )

    def test_parse_captions(self):
        self.assertEqual(
            len(webvtt.from_sbv(PATH_TO_SAMPLES / 'sample.sbv').captions),
            5
        )

    def test_missing_timeframe_line(self):
        self.assertEqual(
            len(webvtt.from_sbv(
                PATH_TO_SAMPLES / 'missing_timeframe.sbv'
                ).captions),
            4
            )

    def test_missing_caption_text(self):
        self.assertTrue(
            webvtt.from_sbv(
                PATH_TO_SAMPLES / 'missing_caption_text.sbv'
                ).captions
            )

    def test_invalid_timestamp(self):
        self.assertEqual(
            len(webvtt.from_sbv(
                PATH_TO_SAMPLES / 'invalid_timeframe.sbv'
                ).captions),
            4
            )

    def test_timestamps_format(self):
        vtt = webvtt.from_sbv(PATH_TO_SAMPLES / 'sample.sbv')
        self.assertEqual(vtt.captions[1].start, '00:00:11.378')
        self.assertEqual(vtt.captions[1].end, '00:00:12.305')

    def test_timestamps_in_seconds(self):
        vtt = webvtt.from_sbv(PATH_TO_SAMPLES / 'sample.sbv')
        self.assertEqual(vtt.captions[1].start_in_seconds, 11)
        self.assertEqual(vtt.captions[1].end_in_seconds, 12)

    def test_get_caption_text(self):
        vtt = webvtt.from_sbv(PATH_TO_SAMPLES / 'sample.sbv')
        self.assertEqual(vtt.captions[1].text, 'Caption text #2')

    def test_get_caption_text_multiline(self):
        vtt = webvtt.from_sbv(PATH_TO_SAMPLES / 'sample.sbv')
        self.assertEqual(
            vtt.captions[2].text,
            'Caption text #3 (line 1)\nCaption text #3 (line 2)'
        )
        self.assertListEqual(
            vtt.captions[2].lines,
            ['Caption text #3 (line 1)', 'Caption text #3 (line 2)']
        )

    def test_convert_from_srt_to_vtt_and_back_gives_same_file(self):
        with tempfile.NamedTemporaryFile('w', suffix='.srt') as f:
            webvtt.from_srt(
                PATH_TO_SAMPLES / 'sample.srt'
                ).save_as_srt(f.name)

            self.assertEqual(
                pathlib.Path(PATH_TO_SAMPLES / 'sample.srt').read_text(),
                pathlib.Path(f.name).read_text()
                )

    def test_save_file_with_bom(self):
        with tempfile.NamedTemporaryFile('r', suffix='.vtt') as f:
            webvtt.read(
                PATH_TO_SAMPLES / 'one_caption.vtt'
                ).save(f.name, add_bom=True)
            self.assertEqual(
                f.read(),
                textwrap.dedent(f'''
                    {CODEC_BOMS['utf-8'].decode()}WEBVTT

                    00:00:00.500 --> 00:00:07.000
                    Caption text #1
                    ''').strip()
                )

    def test_save_file_with_bom_keeps_bom(self):
        with tempfile.NamedTemporaryFile('r', suffix='.vtt') as f:
            webvtt.read(
                PATH_TO_SAMPLES / 'captions_with_bom.vtt'
            ).save(f.name)
            self.assertEqual(
                f.read(),
                textwrap.dedent(f'''
                    {CODEC_BOMS['utf-8'].decode()}WEBVTT

                    00:00:00.500 --> 00:00:07.000
                    Caption text #1

                    00:00:07.000 --> 00:00:11.890
                    Caption text #2

                    00:00:11.890 --> 00:00:16.320
                    Caption text #3

                    00:00:16.320 --> 00:00:21.580
                    Caption text #4
                    ''').strip()
            )

    def test_save_file_with_bom_removes_bom_if_requested(self):
        with tempfile.NamedTemporaryFile('r', suffix='.vtt') as f:
            webvtt.read(
                PATH_TO_SAMPLES / 'captions_with_bom.vtt'
            ).save(f.name, add_bom=False)
            self.assertEqual(
                f.read(),
                textwrap.dedent(f'''
                    WEBVTT

                    00:00:00.500 --> 00:00:07.000
                    Caption text #1

                    00:00:07.000 --> 00:00:11.890
                    Caption text #2

                    00:00:11.890 --> 00:00:16.320
                    Caption text #3

                    00:00:16.320 --> 00:00:21.580
                    Caption text #4
                    ''').strip()
            )

    def test_save_file_with_encoding(self):
        with tempfile.NamedTemporaryFile('rb', suffix='.vtt') as f:
            webvtt.read(
                PATH_TO_SAMPLES / 'one_caption.vtt'
            ).save(f.name,
                   encoding='utf-32-le'
                   )
            self.assertEqual(
                f.read().decode('utf-32-le'),
                textwrap.dedent('''
                    WEBVTT

                    00:00:00.500 --> 00:00:07.000
                    Caption text #1
                    ''').strip()
            )

    def test_save_file_with_encoding_and_bom(self):
        with tempfile.NamedTemporaryFile('rb', suffix='.vtt') as f:
            webvtt.read(
                PATH_TO_SAMPLES / 'one_caption.vtt'
            ).save(f.name,
                   encoding='utf-32-le',
                   add_bom=True
                   )
            self.assertEqual(
                f.read().decode('utf-32-le'),
                textwrap.dedent(f'''
                    {CODEC_BOMS['utf-32-le'].decode('utf-32-le')}WEBVTT

                    00:00:00.500 --> 00:00:07.000
                    Caption text #1
                    ''').strip()
            )

    def test_save_new_file_utf_8_default_encoding_no_bom(self):
        with tempfile.NamedTemporaryFile('r', suffix='.vtt') as f:
            vtt = webvtt.WebVTT()
            vtt.captions.append(
                Caption(start='00:00:00.500',
                        end='00:00:07.000',
                        text='Caption text #1'
                        )
                )
            vtt.save(f.name)
            self.assertEqual(vtt.encoding, 'utf-8')
            self.assertEqual(
                f.read(),
                textwrap.dedent(f'''
                    WEBVTT

                    00:00:00.500 --> 00:00:07.000
                    Caption text #1
                    ''').strip()
                )

    def test_save_new_file_utf_8_default_encoding_with_bom(self):
        with tempfile.NamedTemporaryFile('r', suffix='.vtt') as f:
            vtt = webvtt.WebVTT()
            vtt.captions.append(
                Caption(start='00:00:00.500',
                        end='00:00:07.000',
                        text='Caption text #1'
                        )
                )
            vtt.save(f.name,
                     add_bom=True
                     )
            self.assertEqual(vtt.encoding, 'utf-8')
            self.assertEqual(
                f.read(),
                textwrap.dedent(f'''
                    {CODEC_BOMS['utf-8'].decode()}WEBVTT

                    00:00:00.500 --> 00:00:07.000
                    Caption text #1
                    ''').strip()
                )
