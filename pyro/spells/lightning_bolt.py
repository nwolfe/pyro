import tcod as libtcod
import pyro.utilities
from pyro.engine import Event
from pyro.engine.actions import LosAction
from pyro.spell import ActionSpell, CastResult
from pyro.settings import SPELL_LIGHTNING_BOLT_RANGE, SPELL_LIGHTNING_BOLT_STRENGTH
from pyro.target import Target


class LightningBolt(ActionSpell):
    def __init__(self):
        ActionSpell.__init__(self, 'Lightning Bolt', ActionSpell.TYPE_ATTACK)
        self.range = SPELL_LIGHTNING_BOLT_RANGE
        self.strength = SPELL_LIGHTNING_BOLT_STRENGTH

    def configure(self, settings):
        self.range = settings.get('range', self.range)
        self.strength = settings.get('strength', self.strength)

    def in_range(self, caster, target):
        return caster.pos.distance_to(target.pos) <= self.range

    def requires_target(self):
        return False

    def cast(self, action, caster, target):
        if caster.is_player():
            target = pyro.utilities.closest_monster(action.game, self.range)
            if target is None:
                action.game.log.message('No enemy is close enough to strike.', libtcod.red)
                return CastResult.cancel()
            msg = 'A lightning bolt strikes the {0} with a loud thunderclap! '
            msg += 'The damage is {1} hit points.'
            msg = msg.format(target.name, self.strength)
            action.game.log.message(msg, libtcod.light_blue)
            target.take_damage(action, self.strength, caster)
        else:
            target.actor.take_damage(action, self.strength, caster)
        return CastResult.hit(self.strength)

    def cast_action(self, target):
        return LightningBoltAction(target, self.strength, self.range)


class LightningBoltAction(LosAction):
    def __init__(self, target, damage, range_):
        LosAction.__init__(self, target)
        self._range = range_
        self._damage = damage
        self._needs_target = target is None

    def on_perform(self):
        """Hijack this method to obtain a target if we don't have one.
        Once we have a target, delegate to the real behavior."""
        if self._needs_target:
            nearest = pyro.utilities.closest_monster(self.game, self._range)
            if nearest is None:
                self.game.log.message('No enemy is close enough to strike.', libtcod.red)
                return self.succeed()
            else:
                self.target = Target(actor=nearest)
                self._needs_target = False
        return LosAction.on_perform(self)

    def on_step(self, position):
        # TODO Generalize by adding an "element" type
        self.add_event(Event(Event.TYPE_BOLT, position=position))

    def on_target(self, target):
        target.actor.take_damage(self, self._damage, self.actor)
        msg = 'A lightning bolt strikes the {0} with a loud thunderclap! '
        msg += 'The damage is {1} hit points.'
        msg = msg.format(target.actor.name, self._damage)
        self.game.log.message(msg, libtcod.light_blue)

