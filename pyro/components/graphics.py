import tcod as libtcod
from pyro.component import Component
from pyro.settings import RENDER_ORDER_DEFAULT


class Graphics(Component):
    def __init__(self, glyph=None, color=None, render_order=RENDER_ORDER_DEFAULT, always_visible=False):
        Component.__init__(self, component_type=Graphics)
        self.glyph = glyph
        self.color = color
        self.render_order = render_order
        self.always_visible = always_visible

    def draw(self, console):
        x = self.owner.x
        y = self.owner.y
        always_visible = self.always_visible and self.owner.game.map.is_explored(x, y)
        if always_visible or self.owner.game.map.is_in_fov(x, y):
            # Set the color and then draw the character that
            # represents this object at its position
            libtcod.console_set_default_foreground(console, self.color)
            libtcod.console_put_char(console, x, y, self.glyph, libtcod.BKGND_NONE)

    def clear(self, console):
        # Erase the character that represents this object
        libtcod.console_put_char(console, self.owner.x, self.owner.y, ' ', libtcod.BKGND_NONE)
