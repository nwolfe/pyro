import tcod as libtcod
import pyro.utilities
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
        return False

    def cast(self, action, caster, target):
        if caster.is_player():
            target = pyro.utilities.closest_monster(action.game, self.range)
            if target is None:
                action.game.log.message('No enemy is close enough to strike.', libtcod.red)
                return 'cancelled'
            msg = 'A lightning bolt strikes the {0} with a loud thunderclap! '
            msg += 'The damage is {1} hit points.'
            msg = msg.format(target.name, self.strength)
            action.game.log.message(msg, libtcod.light_blue)
            target.take_damage(action, self.strength, caster)
        else:
            target.actor.take_damage(action, self.strength, caster)
        return self.strength
