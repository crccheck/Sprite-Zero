import unittest
import re
import os
import sys

sys.path[0:0] = os.path.join(os.path.dirname(__file__), '..')
from spritezero import *


class TestRegExpPattern(unittest.TestCase):
    def setUp(self):
        self.converter = SpriteZero()
        self.pattern = self.converter.pattern

    def test_full_with_color_last(self):
        line = "background: url(a/b/c.png) no-repeat scroll 1px 2px #000;"
        match = re.search(self.pattern, line)
        self.assertEqual(('a/b/c.png', '1px', '2px'), match.groups())

    def test_full_with_color_first(self):
        line = "background: #000 url(a/b/c.png) no-repeat scroll 1px 2px;"
        match = re.search(self.pattern, line)
        self.assertEqual(('a/b/c.png', '1px', '2px'), match.groups())

    def test_full_with_no_color(self):
        line = "background: url(a/b/c.png) no-repeat scroll 1px 2px;"
        match = re.search(self.pattern, line)
        self.assertEqual(('a/b/c.png', '1px', '2px'), match.groups())

    def test_basic(self):
        # missing no-repeat but that's not our fault
        line = "background: url(a/b/c.png) 1px 2px;"
        match = re.search(self.pattern, line)
        self.assertEqual(('a/b/c.png', '1px', '2px'), match.groups())

    def test_ignores_other_lines(self):
        line = "background-image: url(a/b/c.png)"
        match = re.search(self.pattern, line)
        self.assertEqual(None, match)

    def test_can_handle_quotes(self):
        #using mixed quotes here to do two tests in one
        line = "background: url(\"a/b/c.png') no-repeat scroll 1px 2px #000;"
        match = re.search(self.pattern, line)
        self.assertEqual(('a/b/c.png', '1px', '2px'), match.groups())

    def test_negative_offsets(self):
        #using mixed quotes here to do two tests in one
        line = "background: url(\"a/b/c.png') no-repeat scroll -1px -2px #000;"
        match = re.search(self.pattern, line)
        self.assertEqual(('a/b/c.png', '-1px', '-2px'), match.groups())

    def test_skip_imports(self):
        line = '@import url("import.css");'
        match = re.search(self.pattern, line)
        self.assertEqual(None, match)

class TestRegExpPatternReplacement(unittest.TestCase):
    def setUp(self):
        self.converter = SpriteZero()
        self.pattern = self.converter.pattern
        self.converter.sprite_png = 'sprite.png'

    def test_trivial_offset(self):
        self.converter.lookup = {'a/b/c.png': {'offset': [0, 0]}}
        line = "background: url(a/b/c.png) no-repeat scroll 1px 2px;"
        self.assertEqual(re.sub(self.pattern, self.converter.replace_css, line),
            'background: url(sprite.png) no-repeat scroll 1px 2px;');

    def test_can_set_offset(self):
        self.converter.lookup = {'a/b/c.png': {'offset': [2, 1]}}
        line = "background: url(a/b/c.png) no-repeat scroll 1px 2px;"
        self.assertEqual(re.sub(self.pattern, self.converter.replace_css, line),
            'background: url(sprite.png) no-repeat scroll -1px 1px;');

class TestConversion(unittest.TestCase):
    def test_string_trivial_case(self):
        converter = SpriteZero()
        converter.sprite_png = "tests/tmp/test-sprite.png"
        test_input = "abcdefghijklmnopqrstuvwxyz"
        test_output = converter.make(test_input)
        self.assertEqual(test_output, test_input)

    def test_string_identity_case(self):
        converter = SpriteZero()
        converter.sprite_png = "tests/tmp/test-sprite.png"
        test_input = "background: url(/tests/resources/40x40.png) no-repeat scroll 1px 2px;"
        test_output = converter.make(test_input)
        self.assertEqual(test_output, 'background: url(tests/tmp/test-sprite.png) no-repeat scroll 1px 2px;')

    def test_file_conversion(self):
        test_css = "tests/resources/test.css"
        with open(test_css, "r") as f:
            converter = SpriteZero()
            converter.sprite_png = "tests/tmp/test.css-sprite.png"
            converter.sprite_uri = "test.css-sprite.png"
            converter.replacement_css = "tests/tmp/test.css"
            converter.make(f)

class TestURIReading(unittest.TestCase):
    def setUp(self):
        self.converter = SpriteZero()

    def test_read_absolute_path(self):
        uri = "/images/someimage.png"
        self.assertEqual(self.converter.uri_to_file(uri), "images/someimage.png")

    def test_read_relative_path(self):
        return
        uri = "../goatse.jpg"
        self.assertRaises(NotImplementedError, self.converter.uri_to_file, uri)

    def test_read_http(self):
        uri = "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.12/themes/trontastic/images/ui-bg_diagonals-small_50_262626_40x40.png"
        f = self.converter.uri_to_file(uri)
        f.read(1)   # seek to 1
        self.assertEqual(f.read(3), "PNG")

    def test_read_https(self):
        uri = "https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.12/themes/trontastic/images/ui-bg_diagonals-small_50_262626_40x40.png"
        f = self.converter.uri_to_file(uri)
        f.read(1)   # seek to 1
        self.assertEqual(f.read(3), "PNG")

    def test_404(self):
        from urllib2 import HTTPError
        uri = "http://localhost/lemonparty.jpg"
        self.assertRaises(HTTPError, self.converter.uri_to_file, uri)

if __name__ == '__main__':
    unittest.main()

