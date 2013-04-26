#!/usr/bin/env python
# coding: utf8

import fontforge
from optparse import OptionParser

def glyph_collect_sub_glyphs(glyph, glyph_names):
    sub_types = ("Substitution", "AltSubs", "MultSubs", "Ligature")
    glyph_names.add(glyph.glyphname)
    for sub in glyph.getPosSub("*"):
        sub_type = sub[1]
        if sub_type in sub_types:
            for name in sub[2:]:
                if name not in glyph_names:
                    glyph_collect_sub_glyphs(glyph.font[name], glyph_names)

def font_collect_references(font, glyph_names):
    refs = set()
    for name in glyph_names:
        glyph = font[name]
        for ref in glyph.references:
            refs.add(ref[0])

    return refs

def font_collect_glyph_names(font, subset):
    glyph_names = set()
    for code in subset:
        if code in font:
            glyph_collect_sub_glyphs(font[code], glyph_names)
        else:
            print "font does not support U+%04X" %code

    return glyph_names

def font_subset(font, subset):
    names = font_collect_glyph_names(font, subset)
    refs = font_collect_references(font, names)
    names.update(refs)

    for glyph in font.glyphs():
        if glyph.glyphname not in names:
            font.removeGlyph(glyph)

if __name__ == "__main__":
    usage = "%prog [options] input output"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--font", dest="filename", help="name of input font file to subset", metavar="FILE")
    parser.add_option("-o", "--output", dest="output", help="name to write subsetted font to", metavar="FILE")
    (options, args) = parser.parse_args()

    filename = options.filename
    output = options.output

    if len(args) >= 1:
        filename = args[0]
    if len(args) >= 2:
        output = args[1]

    if not filename:
        parser.error("You must specify input font filename")
    if not output:
        parser.error("You must specify output font filename")

    s = (ord(u"أ"), ord(u"م"), ord(u"ي"), ord(u"ر"))
    f = fontforge.open(filename)
    font_subset(f, s)
    f.generate(output)
