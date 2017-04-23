from pyro.entity import Entity
from pyro.position import Position


class GameObject(Entity):
    def __init__(self, name=None, components=None, game=None,
                 hp=0, defense=0, power=0):
        Entity.__init__(self, components)
        self.game = game
        self.pos = Position()
        self.name = name
        self.actor = None
        self.__hp__ = hp
        self.__base_max_hp__ = hp
        self.__base_defense__ = defense
        self.__base_power__ = power
