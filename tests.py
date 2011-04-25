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

if __name__ == '__main__':
    unittest.main()

