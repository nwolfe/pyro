import ai as libai
import fighter as libfighter
from settings import *


class Spell:
    def __init__(self, name, range, strength):
        self.name = name
        self.base_range = range
        self.base_strength = strength

    def range(self):
        return self.base_range

    def strength(self):
        return self.base_strength

    def cast(self, caster, target):
        return


class LightningBolt(Spell):
    def __init__(self, name='Lightning Bolt', range=LIGHTNING_RANGE,
                 strength=LIGHTNING_DAMAGE):
        Spell.__init__(self, name, range, strength)

    def cast(self, caster, target):
        target.component(libfighter.Fighter).take_damage(self.strength())


class Heal(Spell):
    def __init__(self, name='Healing', strength=HEAL_AMOUNT):
        Spell.__init__(self, name, 0, strength)

    def cast(self, caster, target):
        target.component(libfighter.Fighter).heal(self.strength())


class Confuse(Spell):
    def __init__(self, name='Confusion', range=CONFUSE_RANGE):
        Spell.__init__(self, name, range, 0)

    def cast(self, caster, target):
        old_ai = target.component(libai.AI)
        new_ai = libai.ConfusedMonster(old_ai)
        target.set_component(libai.AI, new_ai)


def lightning_bolt():
    return LightningBolt(strength=5)
