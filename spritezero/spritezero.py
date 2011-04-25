#!/usr/bin/python
# Assumes non compressed CSS, one definition per line

import re
from optparse import OptionParser
import os

import Image

parser = OptionParser()

PADDING = 10

PATTERN = r'url\([\'"]?([^\'"]+)[\'"]?\).*?(0|\d+px)\s+(0|\d+px)'


def uri_to_file(uri):
    """Translate the web root uri to local path.

    TODO If uri is a url, open a file handler to the resource

    """
    if uri[0] == '/':
        uri = uri[1:]
    return uri

def get_dimensions(image_file):
    image = Image.open(image_file)
    return image.size

def sprite_for_file(f):
    def lookup_to_list(lookup):
        out = []
        for key, value in lookup.iteritems():
            value['uri'] = key
            out.append(value)
        return out
    def replace_css(matchobj):
        groups = matchobj.groups()
        replacement = lookup[groups[0]]
        x = int(re.sub(r"\D+", "", groups[1])) - replacement['offset'][0]
        y = int(re.sub(r"\D+", "", groups[2])) - replacement['offset'][1]
        return "url(/%s) no-repeat scroll %dpx %dpx" % (sprite_png, x, y)

    lookup = {}
    pattern = PATTERN
    for line in f:
        match = re.search(pattern, line)
        if not match:
            continue
        groups = match.groups()
        if groups[0].find('sprite') != -1:
            # yo dawg, i heard you like sprite so i sprited a sprite and it broke
            continue
        if groups[0] not in lookup:
            size = get_dimensions(uri_to_file(groups[0]))
            lookup[groups[0]] = {'size': size,
                                 'length': size[0] * size[1]}

    lookup_list = lookup_to_list(lookup)
    lookup_list.sort(key=lambda x: x['length'])

    width = max([x['size'][0] for x in lookup.values()])     # max width
    height = sum([x['size'][1] for x in lookup.values()]) + PADDING * len(lookup)

    sprite = Image.new("RGBA", (width, height))
    last_y = 0
    for x in lookup_list:
        image = Image.open(uri_to_file(x['uri']))
        offset = (0, last_y)
        sprite.paste(image, offset)
        lookup[x['uri']]['offset'] = offset
        last_y += image.size[1] + PADDING

    sprite.save(sprite_png, "PNG")

    new_f = open(replacement_css, "w")
    f.seek(0)
    for line in f:
        newline = re.sub(pattern, replace_css, line)
        new_f.write(newline)
        if newline != line:
            print line, newline
            print "\n"
    new_f.close()

def replace_css():
    """Replace the old css file with the new one"""
    os.remove(original_css)
    os.rename(replacement_css, original_css)

if __name__ == "__main__":
    options, args = parser.parse_args()
    original_css = args[0]
    replacement_css = original_css + ".tmp"
    sprite_png = original_css + "-sprite.png"
    with open(original_css,"r") as f:
        sprite_for_file(f)
    replace_css()
