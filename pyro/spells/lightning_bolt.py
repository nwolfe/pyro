import libtcodpy as libtcod
from pyro.engine import Event
from pyro.engine.actions import LosAction
from pyro.engine.element import Elements
from pyro.spell import Spell
from pyro.settings import SPELL_LIGHTNING_BOLT_RANGE, SPELL_LIGHTNING_BOLT_STRENGTH


class LightningBolt(Spell):
    def __init__(self):
        Spell.__init__(self, 'Lightning Bolt', Spell.TYPE_ATTACK)
        self.range = SPELL_LIGHTNING_BOLT_RANGE
        self.strength = SPELL_LIGHTNING_BOLT_STRENGTH

    def configure(self, settings):
        self.range = settings.get('range', self.range)
        self.strength = settings.get('strength', self.strength)

    def in_range(self, caster, target):
        return caster.pos.distance_to(target.pos) <= self.range

    def requires_target(self):
        return self.target_nearest(self.range, 'No enemy is close enough to strike.')

    def cast(self, target):
        return LightningBoltAction(target, self.strength)


class LightningBoltAction(LosAction):
    def __init__(self, target, damage):
        LosAction.__init__(self, target)
        self._damage = damage

    def on_step(self, position):
        self.add_event(Event(Event.TYPE_BOLT, element=Elements.LIGHTNING, position=position))

    def on_target(self, target):
        self.game.log.elemental('{1} strike[s] {2} with a bolt of lightning!',
                                Elements.LIGHTNING, self.actor, self.target.actor)
        target.actor.take_damage(self, self._damage, self.actor)

