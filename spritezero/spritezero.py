#!/usr/bin/python
# Assumes non compressed CSS, one definition per line

import re
from optparse import OptionParser
import os
from urllib2 import urlopen
from StringIO import StringIO

import Image


class SpriteZero:
    def __init__(self):
        self.padding = 10
        self.pattern = r'url\([\'"]?([^\'"]+)[\'"]?\).*?(0|-?\d+px)\s+(0|-?\d+px)'
        self.lookup = {}
        self.css_root = ""
        self.verbosity = 0

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

        def place_images(sprite=None):
            """Place images in a box, returns the actual height used"""
            cursor = [0, 0]
            row_height = 0
            last_height = 0
            last_width = 0
            for image in lookup_list:
                im = Image.open(self.uri_to_file(image['uri']))
                # if height is <= last_height: advance cursor to the right
                if (image['size'][1] <= last_height):
                    cursor[0] += last_width + self.padding
                    # check to make sure cursor wasn't advanced off the page
                    if cursor[0] + image['size'][0] > width:
                        cursor[0] = 0
                        cursor[1] += row_height + self.padding
                        row_height = image['size'][1]
                # else: advance cursor to next line
                elif cursor[1]:
                    cursor[0] = 0
                    cursor[1] += row_height + self.padding
                    row_height = image['size'][1]
                # else: we're on the first row
                else:
                    row_height = image['size'][1]
                offset = tuple(cursor)
                if sprite:
                    sprite.paste(im, offset)
                self.lookup[image['uri']]['offset'] = offset
                last_height = image['size'][1]
                last_width = image['size'][0]
            if sprite:
                sprite.save(self.sprite_png, "PNG")
            return cursor[1] + row_height


        lookup_list = lookup_to_list(self.lookup)
        lookup_list.sort(key=lambda x: x['length'], reverse=True)

        width = max([x['size'][0] for x in self.lookup.values()])    # max width
        height = place_images()
        #width *= 2
        sprite = Image.new("RGBA", (width, height))
        place_images(sprite)


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
            if self.verbosity and newline != line:
                print "A>", line, "B>", newline
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
            if self.verbosity:
                print "* css root found:", self.css_root
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
    parser = OptionParser()
    parser.add_option("-i", dest="input", help="input css file")
    parser.add_option("-o", dest="output", help="output css file, DEFAULT: overwrite original")
    parser.add_option("-s", "--sprite", dest="sprite_file", help="Where to put the sprite file")
    parser.add_option("-u", "--sprite_uri", dest="sprite_uri", help="What URI to reference the sprite file")
    parser.add_option("-v", action="store_true", dest="verbosity", help="Verbose mode")

    options, args = parser.parse_args()
    print options
    original_css = options.input
    with open(original_css, "r") as f:
        converter = SpriteZero()
        converter.sprite_png = getattr(options, "sprite_file") or original_css + "-sprite.png"
        if getattr(options,"sprite_uri"):
            converter.sprite_uri = options.sprite_uri
        converter.replacement_css = getattr(options, "output") or original_css + ".tmp"
        converter.verbosity = options.verbosity
        converter.make(f)
    if not getattr(options, "output"):
        converter.replace_old_css()

