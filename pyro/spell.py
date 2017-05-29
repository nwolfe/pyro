import abc


class Spell:
    __metaclass__ = abc.ABCMeta

    TYPE_ATTACK = 'attack'
    TYPE_HEAL = 'heal'

    def __init__(self, name, type_):
        self.name = name
        self.type = type_

    def configure(self, settings):
        pass

    @abc.abstractmethod
    def in_range(self, caster, target):
        pass

    @abc.abstractmethod
    def cast(self, action, caster, target):
        pass

    @abc.abstractmethod
    def player_cast(self, action, player, ui):
        pass
