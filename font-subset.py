#! /usr/bin/python
# coding: utf8

import argparse
import collections
import fontforge
import locale
import sys

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

def font_subset(font, subset):
    chars = set(ord(c) for c in subset)
    allchars = frozenset(chars)
    names = set()

    for glyph in font.glyphs():
        if glyph.unicode in allchars:
            glyph_collect_sub_glyphs(glyph, names)
            chars.discard(glyph.unicode)

    if chars:
        sys.stderr.write("Missing code points: "
                         + " ".join("U+%04X" % c
                                    for c in sorted(chars))
                         + "\n")

    refs = font_collect_references(font, names)
    names.update(refs)

    for glyph in font.glyphs():
        if glyph.glyphname not in names:
            font.removeGlyph(glyph)

def dump_available_glyphs(font):
    table = collections.defaultdict(list)
    for glyph in font.glyphs():
        table[glyph.unicode].append(glyph.glyphname)

    for code, names in sorted(table.items()):
        print "U+%04X: %s" % (code, " ".join(sorted(names)))

def main():
    parser = argparse.ArgumentParser(description="Subset a font.")
    parser.add_argument("font", help="Font file to take the subset of.")
    parser.add_argument("output", help="Output file name.",
                        nargs='?', default='')
    parser.add_argument("chars", help="Characters to include in the subset.",
                        nargs='?', default='')
    args = parser.parse_args()

    f = fontforge.open(args.font)

    if (args.chars and not args.output) or (args.output and not args.chars):
        parser.error("Must specify either both or neither of OUTPUT and CHARS.")

    if not args.chars and not args.output:
        dump_available_glyphs(f)
    else:
        coding = locale.getpreferredencoding()
        font_subset(f, args.chars.decode(coding))
        f.generate(args.output)

    f.close()

if __name__ == '__main__':
    main()

