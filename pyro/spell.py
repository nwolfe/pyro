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
        return self.target_none()

    def target_none(self):
        """Convenience for subclasses with no target."""
        return TargetRequire.NONE

    def target_self(self):
        """Convenience for subclasses that target the caster."""
        return TargetRequire.SELF

    def target_select(self):
        """Convenience for subclasses that ask the player to select a target."""
        return TargetRequire.SELECT
