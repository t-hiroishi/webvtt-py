import os
import unittest
from shutil import rmtree

from webvtt import WebVTTSegmenter
from webvtt import WebVTT

BASE_DIR = os.path.dirname(__file__)
SUBTITLES_DIR = os.path.join(BASE_DIR, 'subtitles')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')


class TestWebVTTSegmenter(unittest.TestCase):

    def setUp(self):
        self.segmenter = WebVTTSegmenter()

    def tearDown(self):
        if os.path.exists(OUTPUT_DIR):
            rmtree(OUTPUT_DIR)

    @staticmethod
    def _get_file(filename: str) -> str:
        return os.path.join(SUBTITLES_DIR, filename)

    def test_total_segments(self):
        # segment with default 10 seconds
        self.segmenter.segment(self._get_file('sample.vtt'), OUTPUT_DIR)
        self.assertEqual(self.segmenter.total_segments, 7)

        # segment with custom 30 seconds
        self.segmenter.segment(self._get_file('sample.vtt'), OUTPUT_DIR, 30)
        self.assertEqual(self.segmenter.total_segments, 3)

    def test_output_folder_is_created(self):
        self.assertFalse(os.path.exists(OUTPUT_DIR))
        self.segmenter.segment(self._get_file('sample.vtt'), OUTPUT_DIR)
        self.assertTrue(os.path.exists(OUTPUT_DIR))

    def test_segmentation_files_exist(self):
        self.segmenter.segment(self._get_file('sample.vtt'), OUTPUT_DIR)
        for i in range(7):
            self.assertTrue(
                os.path.exists(os.path.join(OUTPUT_DIR,
                                            f'fileSequence{i}.webvtt'
                                            )
                               )
            )
        self.assertTrue(os.path.exists(os.path.join(OUTPUT_DIR,
                                                    'prog_index.m3u8'
                                                    )))

    def test_segmentation(self):
        filepath = self._get_file('sample.vtt')
        self.segmenter.segment(filepath, OUTPUT_DIR)

        webvtt = WebVTT.read(filepath)

        # segment 1 should have caption 1 and 2
        self.assertEqual(len(self.segmenter.segments[0]), 2)
        self.assertIn(webvtt.captions[0], self.segmenter.segments[0])
        self.assertIn(webvtt.captions[1], self.segmenter.segments[0])
        # segment 2 should have caption 2 again (overlap), 3 and 4
        self.assertEqual(len(self.segmenter.segments[1]), 3)
        self.assertIn(webvtt.captions[2], self.segmenter.segments[1])
        self.assertIn(webvtt.captions[3], self.segmenter.segments[1])
        # segment 3 should have caption 4 again (overlap), 5, 6 and 7
        self.assertEqual(len(self.segmenter.segments[2]), 4)
        self.assertIn(webvtt.captions[3], self.segmenter.segments[2])
        self.assertIn(webvtt.captions[4], self.segmenter.segments[2])
        self.assertIn(webvtt.captions[5], self.segmenter.segments[2])
        self.assertIn(webvtt.captions[6], self.segmenter.segments[2])
        # segment 4 should have caption 7 again (overlap), 8, 9 and 10
        self.assertEqual(len(self.segmenter.segments[3]), 4)
        self.assertIn(webvtt.captions[6], self.segmenter.segments[3])
        self.assertIn(webvtt.captions[7], self.segmenter.segments[3])
        self.assertIn(webvtt.captions[8], self.segmenter.segments[3])
        self.assertIn(webvtt.captions[9], self.segmenter.segments[3])
        # segment 5 should have caption 10 again (overlap), 11 and 12
        self.assertEqual(len(self.segmenter.segments[4]), 3)
        self.assertIn(webvtt.captions[9], self.segmenter.segments[4])
        self.assertIn(webvtt.captions[10], self.segmenter.segments[4])
        self.assertIn(webvtt.captions[11], self.segmenter.segments[4])
        # segment 6 should have caption 12 again (overlap), 13, 14 and 15
        self.assertEqual(len(self.segmenter.segments[5]), 4)
        self.assertIn(webvtt.captions[11], self.segmenter.segments[5])
        self.assertIn(webvtt.captions[12], self.segmenter.segments[5])
        self.assertIn(webvtt.captions[13], self.segmenter.segments[5])
        self.assertIn(webvtt.captions[14], self.segmenter.segments[5])
        # segment 7 should have caption 15 again (overlap) and 16
        self.assertEqual(len(self.segmenter.segments[6]), 2)
        self.assertIn(webvtt.captions[14], self.segmenter.segments[6])
        self.assertIn(webvtt.captions[15], self.segmenter.segments[6])

    def test_segment_content(self):
        self.segmenter.segment(self._get_file('sample.vtt'), OUTPUT_DIR, 10)

        with open(
                os.path.join(OUTPUT_DIR, 'fileSequence0.webvtt'),
                'r',
                encoding='utf-8'
                ) as f:
            lines = [line.rstrip() for line in f.readlines()]

        expected_lines = [
            'WEBVTT',
            'X-TIMESTAMP-MAP=MPEGTS:900000,LOCAL:00:00:00.000',
            '',
            '00:00:00.500 --> 00:00:07.000',
            'Caption text #1',
            '',
            '00:00:07.000 --> 00:00:11.890',
            'Caption text #2'
        ]

        self.assertListEqual(lines, expected_lines)

    def test_manifest_content(self):
        self.segmenter.segment(self._get_file('sample.vtt'), OUTPUT_DIR, 10)

        with open(
                os.path.join(OUTPUT_DIR, 'prog_index.m3u8'),
                'r',
                encoding='utf-8'
                ) as f:
            lines = [line.rstrip() for line in f.readlines()]

            expected_lines = [
                '#EXTM3U',
                '#EXT-X-TARGETDURATION:{}'.format(self.segmenter.seconds),
                '#EXT-X-VERSION:3',
                '#EXT-X-PLAYLIST-TYPE:VOD',
                ]

            for i in range(7):
                expected_lines.extend([
                    '#EXTINF:30.00000',
                    'fileSequence{}.webvtt'.format(i)
                ])

            expected_lines.append('#EXT-X-ENDLIST')

            for index, line in enumerate(expected_lines):
                self.assertEqual(lines[index], line)

    def test_customize_mpegts(self):
        self.segmenter.segment(self._get_file('sample.vtt'),
                               OUTPUT_DIR,
                               mpegts=800000
                               )

        with open(
                os.path.join(OUTPUT_DIR, 'fileSequence0.webvtt'),
                'r',
                encoding='utf-8'
                ) as f:
            lines = f.readlines()
            self.assertIn('MPEGTS:800000', lines[1])

    def test_segment_from_file(self):
        self.segmenter.segment(
            os.path.join(SUBTITLES_DIR, 'sample.vtt'), OUTPUT_DIR
            ),
        self.assertEqual(self.segmenter.total_segments, 7)

    def test_segment_with_no_captions(self):
        self.segmenter.segment(
            os.path.join(SUBTITLES_DIR, 'no_captions.vtt'), OUTPUT_DIR
            ),
        self.assertEqual(self.segmenter.total_segments, 0)

    def test_total_segments_readonly(self):
        self.assertRaises(
            AttributeError,
            setattr,
            WebVTTSegmenter(),
            'total_segments',
            5
        )
