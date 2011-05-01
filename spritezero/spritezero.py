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
        self.padding = 10
        self.pattern = r'url\([\'"]?([^\'"]+)[\'"]?\).*?(0|-?\d+px)\s+(0|-?\d+px)'
        self.lookup = {}
        self.css_root = ""

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
            return self.css_root + uri

    def get_dimensions(self, image_file):
        image = Image.open(image_file)
        return image.size

    def replace_css(self, matchobj):
        """replacement function that returns sprite file and proper offsets"""
        groups = matchobj.groups()
        replacement = self.lookup[groups[0]]
        x = int(re.sub(r"\D+", "", groups[1])) - replacement['offset'][0]
        y = int(re.sub(r"\D+", "", groups[2])) - replacement['offset'][1]
        return "url(%s) no-repeat scroll %dpx %dpx" %\
            (getattr(self, 'sprite_uri', self.sprite_png), x, y)

    def generate_image_inventory(self):
        """First pass through the file, get image sizes"""
        f = self.input_file
        for line in f:
            match = re.search(self.pattern, line)
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

    def generate_sprite_image(self):
        def lookup_to_list(lookup):
            out = []
            for key, value in lookup.iteritems():
                value['uri'] = key
                out.append(value)
            return out

        lookup_list = lookup_to_list(self.lookup)
        lookup_list.sort(key=lambda x: x['length'])

        width = max([x['size'][0] for x in self.lookup.values()])    # max width
        height = sum([x['size'][1] for x in self.lookup.values()]) + \
                 self.padding * len(self.lookup)

        sprite = Image.new("RGBA", (width, height))
        last_y = 0
        for x in lookup_list:
            image = Image.open(self.uri_to_file(x['uri']))
            offset = (0, last_y)
            sprite.paste(image, offset)
            self.lookup[x['uri']]['offset'] = offset
            last_y += image.size[1] + self.padding

        sprite.save(self.sprite_png, "PNG")

    def generate_new_css(self):
        """Second pass, create css sprite"""
        f = self.input_file
        if self.return_type == "string":
            new_f = StringIO()
        else:
            new_f = open(self.replacement_css, "w")
        f.seek(0)
        for line in f:
            try:
                newline = re.sub(self.pattern, self.replace_css, line)
            except KeyError:
                newline = line
            new_f.write(newline)
            if newline != line:
                print line, newline
                print "\n"
        return new_f

    def make(self, f):
        """
        main function, takes an input file and returns a new file using sprites

        """
        self.return_type = "file" if isinstance(f, file) else "string"
        if self.return_type == "string":
            f = StringIO(f)
        else:
            self.css_root = os.path.dirname(f.name) + '/'
            print "root found", self.css_root
        self.input_file = f

        self.generate_image_inventory()

        if len(self.lookup):
            self.generate_sprite_image()

        new_f = self.generate_new_css()

        if self.return_type == "string":
            new_f.seek(0)
            return new_f.read()
        new_f.close()

    def replace_old_css(self):
        """Replace the old css file with the new one"""
        os.remove(original_css)
        os.rename(self.replacement_css, original_css)

if __name__ == "__main__":
    options, args = parser.parse_args()
    original_css = args[0]
    with open(original_css, "r") as f:
        converter = SpriteZero()
        converter.sprite_png = original_css + "-sprite.png"
        converter.replacement_css = original_css + ".tmp"
        converter.make(f)
    converter.replace_old_css()

