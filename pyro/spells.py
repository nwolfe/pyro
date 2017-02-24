import libtcodpy as libtcod
from pyro.components.ai import AI
from pyro.components.fighter import Fighter
from pyro.components.projectile import Projectile
from pyro.gameobject import GameObject
from pyro.ai.confused import Confused
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

    def cast(self, caster, target):
        return


class LightningBolt(Spell):
    def __init__(self, name='Lightning Bolt', spell_range=LIGHTNING_RANGE,
                 strength=LIGHTNING_DAMAGE):
        Spell.__init__(self, name, spell_range, strength)

    def cast(self, caster, target):
        def on_hit(t):
            t.component(Fighter).take_damage(self.strength())
        bolt = Projectile(source=caster, target=target, on_hit_fn=on_hit)
        obj = GameObject(name='Bolt of Lightning', glyph='*',
                         components={Projectile: bolt},
                         color=libtcod.blue, blocks=False, game=caster.game)
        caster.game.objects.append(obj)


class Heal(Spell):
    def __init__(self, name='Healing', strength=HEAL_AMOUNT):
        Spell.__init__(self, name, 0, strength)

    def cast(self, caster, target):
        target.component(Fighter).heal(self.strength())


class Confuse(Spell):
    def __init__(self, name='Confusion', spell_range=CONFUSE_RANGE):
        Spell.__init__(self, name, spell_range, 0)

    def cast(self, caster, target):
        old_ai = target.component(AI)
        new_ai = Confused(old_ai)
        target.set_component(AI, new_ai)


def lightning_bolt():
    return LightningBolt(strength=5)
