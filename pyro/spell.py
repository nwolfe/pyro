import abc


class SpellType:
    ATTACK = 'attack'
    HEAL = 'heal'


class Spell:
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, spell_type):
        self.name = name
        self.type = spell_type

    def configure(self, settings):
        pass

    @abc.abstractmethod
    def in_range(self, caster, target):
        pass

    @abc.abstractmethod
    def cast(self, action, caster, target):
        pass

    @abc.abstractmethod
    def player_cast(self, action, player, game, ui):
        pass
