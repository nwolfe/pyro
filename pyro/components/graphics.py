from pyro.component import Component
from pyro.settings import RENDER_ORDER_DEFAULT


class Graphics(Component):
    def __init__(self, glyph=None, color=None, render_order=RENDER_ORDER_DEFAULT, always_visible=False):
        Component.__init__(self, component_type=Graphics)
        self.glyph = glyph
        self.color = color
        self.render_order = render_order
        self.always_visible = always_visible
