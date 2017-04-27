from pyro.component import Component


class Graphics(Component):
    def __init__(self, glyph=None, color=None):
        Component.__init__(self, component_type=Graphics)
        self.glyph = glyph
        self.color = color
