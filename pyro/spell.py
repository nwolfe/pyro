import abc
from pyro.target import TargetRequire


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

    def cast(self, target):
        """Returns an Action."""
        pass

    def requires_target(self):
        """Override to declare target requirements."""
        return TargetRequire.NONE

    def target_self(self):
        """Convenience for subclasses that target the caster."""
        return TargetRequire.SELF

    def target_select(self, range_=None):
        """Convenience for subclasses that ask the player to select a target."""
        return TargetRequire(TargetRequire.TYPE_SELECT, range_)

    def target_nearest(self, range_=None, not_found_message=None):
        """Convenience for subclasses that target the nearest monster."""
        return TargetRequire(TargetRequire.TYPE_NEAREST, range_, not_found_message)
