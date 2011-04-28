import unittest
import re

from spritezero import *

class TestRegExpPattern(unittest.TestCase):
    def test_full_with_color_last(self):
        line = "background: url(a/b/c.png) no-repeat scroll 1px 2px #000;"
        match = re.search(PATTERN, line)
        self.assertEqual(('a/b/c.png', '1px', '2px'), match.groups())

    def test_full_with_color_first(self):
        line = "background: #000 url(a/b/c.png) no-repeat scroll 1px 2px;"
        match = re.search(PATTERN, line)
        self.assertEqual(('a/b/c.png', '1px', '2px'), match.groups())

    def test_full_with_no_color(self):
        line = "background: url(a/b/c.png) no-repeat scroll 1px 2px;"
        match = re.search(PATTERN, line)
        self.assertEqual(('a/b/c.png', '1px', '2px'), match.groups())

    def test_basic(self):
        # missing no-repeat but that's not our fault
        line = "background: url(a/b/c.png) 1px 2px;"
        match = re.search(PATTERN, line)
        self.assertEqual(('a/b/c.png', '1px', '2px'), match.groups())

    def test_ignores_other_lines(self):
        line = "background-image: url(a/b/c.png)"
        match = re.search(PATTERN, line)
        self.assertEqual(None, match)

    def test_can_handle_quotes(self):
        #using mixed quotes here to do two tests in one
        line = "background: url(\"a/b/c.png') no-repeat scroll 1px 2px #000;"
        match = re.search(PATTERN, line)
        self.assertEqual(('a/b/c.png', '1px', '2px'), match.groups())

    def test_negative_offsets(self):
        #using mixed quotes here to do two tests in one
        line = "background: url(\"a/b/c.png') no-repeat scroll -1px -2px #000;"
        match = re.search(PATTERN, line)
        self.assertEqual(('a/b/c.png', '-1px', '-2px'), match.groups())

class TestURIReading(unittest.TestCase):
    def test_read_absolute_path(self):
        uri = "/images/someimage.png"
        self.assertEqual(uri_to_file(uri), "images/someimage.png")

    def test_read_http(self):
        uri = "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.12/themes/trontastic/images/ui-bg_diagonals-small_50_262626_40x40.png"
        f = uri_to_file(uri)
        f.read(1)   # seek to 1
        self.assertEqual(f.read(3), "PNG")

    def test_read_https(self):
        uri = "https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.12/themes/trontastic/images/ui-bg_diagonals-small_50_262626_40x40.png"
        f = uri_to_file(uri)
        f.read(1)   # seek to 1
        self.assertEqual(f.read(3), "PNG")

    def test_404(self):
        from urllib2 import HTTPError
        uri = "http://localhost/lemonparty.jpg"
        self.assertRaises(HTTPError, uri_to_file, uri)

    def test_not_implemented(self):
        uri = "../goatse.jpg"
        self.assertRaises(NotImplementedError, uri_to_file, uri)

if __name__ == '__main__':
    unittest.main()

