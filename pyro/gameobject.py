import math
import tcod as libtcod
from pyro.events import EventSource
from pyro.settings import RENDER_ORDER_DEFAULT


class GameObject(EventSource):
    def __init__(self, x=0, y=0, glyph=None, name=None, color=None, blocks=False,
                 render_order=RENDER_ORDER_DEFAULT, always_visible=False, components=None,
                 game=None, listeners=None):
        EventSource.__init__(self, listeners)
        self.x = x
        self.y = y
        self.glyph = glyph
        self.color = color
        self.name = name
        self.render_order = render_order
        self.always_visible = always_visible
        self.blocks = blocks
        self.game = game

        self.components = {}
        if components:
            for comp in components:
                self.set_component(comp)

    def component(self, component_type):
        return self.components.get(component_type)

    def set_component(self, component):
        self.remove_component(component.type)
        self.components[component.type] = component
        component.set_owner(self)

    def remove_component(self, component_type):
        if component_type in self.components:
            self.components.pop(component_type).remove_owner(self)

    def add_to_game(self):
        self.game.add_object(self)

    def remove_from_game(self):
        self.game.remove_object(self)

    def draw(self, console):
        always_visible = self.always_visible and self.game.map.is_explored(self.x, self.y)
        if always_visible or self.game.map.is_in_fov(self.x, self.y):
            # Set the color and then draw the character that
            # represents this object at its position
            libtcod.console_set_default_foreground(console, self.color)
            libtcod.console_put_char(console, self.x, self.y, self.glyph,
                                     libtcod.BKGND_NONE)

    def clear(self, console):
        # Erase the character that represents this object
        libtcod.console_put_char(console, self.x, self.y, ' ',
                                 libtcod.BKGND_NONE)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

