import pyro.components.ai as libai
import pyro.components.fighter as libfighter
import pyro.ai.confused as libconf
from pyro.settings import *


class Spell:
    def __init__(self, name, spell_range, strength):
        self.name = name
        self.base_range = spell_range
        self.base_strength = strength

    def range(self):
        return self.base_range

    def strength(self):
        return self.base_strength

    def cast(self, caster, targets):
        return


class LightningBolt(Spell):
    def __init__(self, name='Lightning Bolt', spell_range=LIGHTNING_RANGE,
                 strength=LIGHTNING_DAMAGE):
        Spell.__init__(self, name, spell_range, strength)

    def cast(self, caster, targets):
        targets[0].component(libfighter.Fighter).take_damage(self.strength())


class Heal(Spell):
    def __init__(self, name='Healing', strength=HEAL_AMOUNT):
        Spell.__init__(self, name, 0, strength)

    def cast(self, caster, targets):
        targets[0].component(libfighter.Fighter).heal(self.strength())


class Confuse(Spell):
    def __init__(self, name='Confusion', spell_range=CONFUSE_RANGE):
        Spell.__init__(self, name, spell_range, 0)

    def cast(self, caster, targets):
        old_ai = targets[0].component(libai.AI)
        new_ai = libconf.Confused(old_ai)
        targets[0].set_component(libai.AI, new_ai)


def lightning_bolt():
    return LightningBolt(strength=5)
