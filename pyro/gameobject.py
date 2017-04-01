import math
from pyro.events import EventSource


class GameObject(EventSource):
    def __init__(self, x=0, y=0, name=None, blocks=False,
                 components=None, game=None, listeners=None):
        EventSource.__init__(self, listeners)
        self.x = x
        self.y = y
        self.name = name
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

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

