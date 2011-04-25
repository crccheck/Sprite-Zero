Sprite Zero
===========
Sprite zero is an extremely simple script that automates creating css sprites.
It will create a sprite file for every css file you feed it.
If you need a sprite file that spans multiple files, you'll have to concatenate them yourself.

To make sure images aren't sprited, you can do any of the following:

* don't use the background shortcut notation
* instead of setting the position at `0 0`, use `top left`
* in fact, the script will skip every non-pixel offset

This is *very* alpha

Usage
-----
Run this script from the root of your web folder, pass the location of a CSS
file as an argument. `python <path_to_spritezero.py> <path_to_css_file>`

Your old CSS file will be replaced. To revert, do `git reset --hard HEAD`


Other similar programs:
-----------------------
I searched for some similar programs written in Python, but I couldn't find
one that did exactly what I had in mind. There seem to be a lot more written
for RoR, but I wanted to stay in Python. These are some of the other projects
I found that seemed interesting:

*   [django-media-bundler](https://github.com/eroh92/django-media-bundler)
    Does too much

*   [django-elves](https://github.com/asokoloski/django-elves)
    Too much configuration

*   [sprite_generator](https://github.com/jgallen23/sprite_generator)


