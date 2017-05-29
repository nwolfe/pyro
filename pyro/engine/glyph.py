from collections import namedtuple


_Glyph = namedtuple('Glyph', 'char fg_color bg_color')


def glyph(char, fg_color, bg_color=None):
    return _Glyph(char, fg_color, bg_color if bg_color else fg_color)
