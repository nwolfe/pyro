

class Glyph:
    def __init__(self, char, fg_color, bg_color=None):
        self.char = char
        self.fg_color = fg_color
        self.bg_color = bg_color if bg_color else fg_color
