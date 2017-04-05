from pyro.entity import Entity
from pyro.position import Position


class GameObject(Entity):
    def __init__(self, name=None, blocks=False, components=None, game=None):
        self.game = game
        self.pos = Position()
        self.name = name
        self.blocks = blocks
        Entity.__init__(self, components)
