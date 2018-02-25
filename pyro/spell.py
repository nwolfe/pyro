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

    def cast_action(self, target):
        pass

    def requires_target(self):
        return True


class CastResult:

    TYPE_HIT = 'hit'
    TYPE_MISS = 'miss'
    TYPE_CANCEL = 'cancel'
    TYPE_INVALID_TARGET = 'invalid_target'

    def __init__(self, type_, damage=None):
        self.type = type_
        self.damage = damage

    @classmethod
    def hit(cls, damage):
        return CastResult(CastResult.TYPE_HIT, damage)

    @classmethod
    def miss(cls):
        return CastResult(CastResult.TYPE_MISS)

    @classmethod
    def cancel(cls):
        return CastResult(CastResult.TYPE_CANCEL)

    @classmethod
    def invalid_target(cls):
        return CastResult(CastResult.TYPE_INVALID_TARGET)
