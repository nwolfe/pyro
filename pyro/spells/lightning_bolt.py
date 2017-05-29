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

    def cast(self, action, caster, target):
        target.take_damage(action, self.strength, caster)
        return self.strength

    def player_cast(self, action, player, ui):
        # Find the closest enemy (inside a maximum range) and damage it
        monster = pyro.utilities.closest_monster(action.game, self.range)
        if monster is None:
            action.game.log.message('No enemy is close enough to strike.', libtcod.red)
            return 'cancelled'

        # Zap it!
        msg = 'A lightning bolt strikes the {0} with a loud thunderclap! '
        msg += 'The damage is {1} hit points.'
        msg = msg.format(monster.name, self.strength)
        action.game.log.message(msg, libtcod.light_blue)
        self.cast(action, player, monster)
