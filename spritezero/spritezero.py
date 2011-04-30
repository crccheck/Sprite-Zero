#!/usr/bin/python
# Assumes non compressed CSS, one definition per line

import re
from optparse import OptionParser
import os
from urllib2 import urlopen
from StringIO import StringIO

import Image


parser = OptionParser()

class SpriteZero:
    def __init__(self):
        self.PADDING = 10
        self.PATTERN = r'url\([\'"]?([^\'"]+)[\'"]?\).*?(0|-?\d+px)\s+(0|-?\d+px)'
        self.lookup = {}

    def uri_to_file(self, uri):
        """Translate the web root uri to local path.

        TODO If uri is a url, open a file handler to the resource

        """
        if uri[0] == '/':
            return uri[1:]
        elif re.match(r"http", uri):
            # TODO close files
            return urlopen(uri)
        else:
            raise NotImplementedError("Can't handle uri of type: url(%s) yet" % uri)

    def get_dimensions(self, image_file):
        image = Image.open(image_file)
        return image.size

    def replace_css(self, matchobj):
        """replacement function that returns sprite file and proper offsets"""
        groups = matchobj.groups()
        replacement = self.lookup[groups[0]]
        x = int(re.sub(r"\D+", "", groups[1])) - replacement['offset'][0]
        y = int(re.sub(r"\D+", "", groups[2])) - replacement['offset'][1]
        return "url(/%s) no-repeat scroll %dpx %dpx" % (self.sprite_png, x, y)

    def sprite_for_file(self, f):
        def lookup_to_list(lookup):
            out = []
            for key, value in lookup.iteritems():
                value['uri'] = key
                out.append(value)
            return out

        return_type = "file" if isinstance(f, file) else "string"

        if return_type == "string":
            f = StringIO(f)

        pattern = self.PATTERN
        for line in f:
            match = re.search(pattern, line)
            if not match:
                continue
            groups = match.groups()
            if groups[0].find('sprite') != -1:
                # yo dawg, i heard you like sprite so i sprited a sprite and it broke
                continue
            if groups[0] not in self.lookup:
                size = self.get_dimensions(self.uri_to_file(groups[0]))
                self.lookup[groups[0]] = {'size': size,
                                          'length': size[0] * size[1]}

        if len(self.lookup):
            lookup_list = lookup_to_list(self.lookup)
            lookup_list.sort(key=lambda x: x['length'])

            width = max([x['size'][0] for x in self.lookup.values()])    # max width
            height = sum([x['size'][1] for x in self.lookup.values()]) + \
                     self.PADDING * len(self.lookup)

            sprite = Image.new("RGBA", (width, height))
            last_y = 0
            for x in lookup_list:
                image = Image.open(self.uri_to_file(x['uri']))
                offset = (0, last_y)
                sprite.paste(image, offset)
                self.lookup[x['uri']]['offset'] = offset
                last_y += image.size[1] + self.PADDING

            sprite.save(self.sprite_png, "PNG")


        if return_type == "string":
            new_f = StringIO()
        else:
            new_f = open(replacement_css, "w")
        f.seek(0)
        for line in f:
            try:
                newline = re.sub(pattern, self.replace_css, line)
            except KeyError:
                newline = line
            new_f.write(newline)
            if newline != line:
                print line, newline
                print "\n"
        if return_type == "string":
            new_f.seek(0)
            return new_f.read()
        new_f.close()

    def replace_old_css(self):
        """Replace the old css file with the new one"""
        os.remove(original_css)
        os.rename(replacement_css, original_css)

if __name__ == "__main__":
    options, args = parser.parse_args()
    original_css = args[0]
    replacement_css = original_css + ".tmp"
    with open(original_css, "r") as f:
        converter = SpriteZero()
        converter.sprite_png = original_css + "-sprite.png"
        converter.sprite_for_file(f)
    converter.replace_old_css()

