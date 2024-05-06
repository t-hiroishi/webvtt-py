import unittest
from datetime import time

from webvtt import Caption, Style
from webvtt.errors import MalformedCaptionError


class TestCaption(unittest.TestCase):

    def test_instantiation(self):
        caption = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text='Hello test!',
            identifier='A test caption'
            )
        self.assertEqual(caption.start, '00:00:07.000')
        self.assertEqual(caption.end, '00:00:11.890')
        self.assertEqual(caption.text, 'Hello test!')
        self.assertEqual(caption.identifier, 'A test caption')

    def test_timestamp_accept_time(self):
        caption = Caption(
            start=time(hour=0, minute=0, second=7, microsecond=0),
            end=time(hour=0, minute=0, second=11, microsecond=890000),
            text='Hello test!',
            identifier='A test caption'
            )
        self.assertEqual(caption.start, '00:00:07.000')
        self.assertEqual(caption.end, '00:00:11.890')

    def test_identifier_is_optional(self):
        caption = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text='Hello test!',
            )
        self.assertIsNone(caption.identifier)

    def test_multi_lines(self):
        caption = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text='Hello test!\nThis is the second line',
            identifier='A test caption'
            )
        self.assertEqual(caption.text, 'Hello test!\nThis is the second line')
        self.assertListEqual(
            caption.lines,
            ['Hello test!', 'This is the second line']
            )

    def test_multi_lines_accepts_list(self):
        caption = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text=['Hello test!', 'This is the second line'],
            identifier='A test caption'
            )
        self.assertEqual(caption.text, 'Hello test!\nThis is the second line')
        self.assertListEqual(
            caption.lines,
            ['Hello test!', 'This is the second line']
            )

    def test_cuetags(self):
        caption = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text=[
                'Hello <c.colorE5E5E5>test</c>!',
                'This is the <c.colorE5E5E5>second</c> line'
                ],
            identifier='A test caption'
            )
        self.assertEqual(caption.text, 'Hello test!\nThis is the second line')
        self.assertEqual(
            caption.raw_text,
            'Hello <c.colorE5E5E5>test</c>!\n'
            'This is the <c.colorE5E5E5>second</c> line'
            )

    def test_in_seconds(self):
        caption = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text=['Hello test!', 'This is the second line'],
            identifier='A test caption'
            )
        self.assertEqual(caption.start_in_seconds, 7)
        self.assertEqual(caption.end_in_seconds, 11)

    def test_wrong_start_timestamp(self):
        self.assertRaises(
            MalformedCaptionError,
            Caption,
            start='1234',
            end='00:00:11.890',
            text='Hello Test!'
        )

    def test_wrong_type_start_timestamp(self):
        self.assertRaises(
            TypeError,
            Caption,
            start=1234,
            end='00:00:11.890',
            text='Hello Test!'
        )

    def test_wrong_end_timestamp(self):
        self.assertRaises(
            MalformedCaptionError,
            Caption,
            start='00:00:07.000',
            end='1234',
            text='Hello Test!'
        )

    def test_wrong_type_end_timestamp(self):
        self.assertRaises(
            TypeError,
            Caption,
            start='00:00:07.000',
            end=1234,
            text='Hello Test!'
        )

    def test_equality(self):
        caption1 = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text='Hello test!',
            identifier='A test caption'
            )

        caption2 = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text='Hello test!',
            identifier='A test caption'
            )

        self.assertTrue(caption1 == caption2)

        caption1 = Caption(
            start='00:00:02.000',
            end='00:00:11.890',
            text='Hello test!',
            identifier='A test caption'
            )

        caption2 = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text='Hello test!',
            identifier='A test caption'
            )

        self.assertFalse(caption1 == caption2)

        self.assertFalse(
            Caption(
                start='00:00:07.000',
                end='00:00:11.890',
                text='Hello test!',
                identifier='A test caption'
            ) == 1234
        )

    def test_repr(self):
        caption = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text='Hello test!',
            identifier='A test caption'
        )

        self.assertEqual(
            repr(caption),
            "<Caption start='00:00:07.000' end='00:00:11.890' "
            "text='Hello test!' identifier='A test caption'>"
            )

    def test_str(self):
        caption = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text='Hello test!',
            identifier='A test caption'
        )

        self.assertEqual(
            str(caption),
            '00:00:07.000 00:00:11.890 Hello test!'
            )

    def test_accept_comments(self):
        caption = Caption(
            start='00:00:07.000',
            end='00:00:11.890',
            text='Hello test!',
            identifier='A test caption'
        )
        caption.comments.append('One comment')
        caption.comments.append('Another comment')

        self.assertListEqual(
            caption.comments,
            ['One comment', 'Another comment']
        )

    def test_timestamp_update(self):
        c = Caption('00:00:00.500', '00:00:07.000')
        c.start = '00:00:01.750'
        c.end = '00:00:08.250'

        self.assertEqual(c.start, '00:00:01.750')
        self.assertEqual(c.end, '00:00:08.250')

    def test_timestamp_format(self):
        c = Caption('01:02:03.400', '02:03:04.500')
        self.assertEqual(c.start, '01:02:03.400')
        self.assertEqual(c.end, '02:03:04.500')

        c = Caption('02:03.400', '03:04.500')
        self.assertEqual(c.start, '00:02:03.400')
        self.assertEqual(c.end, '00:03:04.500')

    def test_update_text(self):
        c = Caption(text='Caption line #1')
        c.text = 'Caption line #1 updated'
        self.assertEqual(
            c.text,
            'Caption line #1 updated'
        )

    def test_update_text_multiline(self):
        c = Caption(text='Caption line #1')
        c.text = 'Caption line #1\nCaption line #2'

        self.assertEqual(
            len(c.lines),
            2
        )

        self.assertEqual(
            c.text,
            'Caption line #1\nCaption line #2'
        )

    def test_update_text_wrong_type(self):
        c = Caption(text='Caption line #1')

        self.assertRaises(
            AttributeError,
            setattr,
            c,
            'text',
            123
        )

    def test_manipulate_lines(self):
        c = Caption(text=['Caption line #1', 'Caption line #2'])
        c.lines[0] = 'Caption line #1 updated'
        self.assertEqual(
            c.lines[0],
            'Caption line #1 updated'
        )

    def test_malformed_start_timestamp(self):
        self.assertRaises(
            MalformedCaptionError,
            Caption,
            '01:00'
        )


class TestStyle(unittest.TestCase):

    def test_instantiation(self):
        style = Style(text='::cue(b) {\ncolor: peachpuff;\n}')
        self.assertEqual(style.text, '::cue(b) {\ncolor: peachpuff;\n}')
        self.assertListEqual(
            style.lines,
            ['::cue(b) {', 'color: peachpuff;', '}']
            )

    def test_text_accept_list_of_strings(self):
        style = Style(text=['::cue(b) {', 'color: peachpuff;', '}'])
        self.assertEqual(style.text, '::cue(b) {\ncolor: peachpuff;\n}')
        self.assertListEqual(
            style.lines,
            ['::cue(b) {', 'color: peachpuff;', '}']
            )

    def test_accept_comments(self):
        style = Style(text='::cue(b) {\ncolor: peachpuff;\n}')
        style.comments.append('One comment')
        style.comments.append('Another comment')

        self.assertListEqual(
            style.comments,
            ['One comment', 'Another comment']
        )

    def test_get_text(self):
        style = Style(['::cue(b) {', '  color: peachpuff;', '}'])
        self.assertEqual(
            style.text,
            '::cue(b) {\n  color: peachpuff;\n}'
        )
