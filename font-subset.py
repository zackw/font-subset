#!/usr/bin/env python
# coding: utf8

import fontforge
import sys

def glyph_collect_sub_glyphs(glyph, glyph_names):
    sub_types = ("Substitution", "AltSubs", "MultSubs", "Ligature")
    for sub in glyph.getPosSub("*"):
        sub_type = sub[1]
        if sub_type in sub_types:
            for name in sub[2:]:
                if name not in glyph_names:
                    glyph_names.add(name)
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
            glyph = font[code]
            glyph_names.add(glyph.glyphname)
            glyph_collect_sub_glyphs(glyph, glyph_names)
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
    f = fontforge.open(sys.argv[1])
    s = (ord(u"أ"), ord(u"م"), ord(u"ي"), ord(u"ر"))
    font_subset(f, s)
    f.save("subset.sfd")
    f.generate("subset.ttf")
