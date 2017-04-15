from pyro.entity import Entity
from pyro.position import Position


class GameObject(Entity):
    def __init__(self, name=None, components=None, game=None):
        Entity.__init__(self, components)
        self.game = game
        self.pos = Position()
        self.name = name
        self.actor = None
