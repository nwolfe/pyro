import tcod as libtcod
import pyro.utilities
from pyro.components import AI
from pyro.spell import Spell, SpellType
from pyro.settings import SPELL_CONFUSE_RANGE, SPELL_CONFUSE_TURNS


class Confuse(Spell):
    def __init__(self):
        Spell.__init__(self, 'Confusion', SpellType.ATTACK)
        self.range = SPELL_CONFUSE_RANGE
        self.num_turns = SPELL_CONFUSE_TURNS

    def configure(self, settings):
        self.range = settings.get('range', self.range)
        self.num_turns = settings.get('turns', self.num_turns)

    def in_range(self, caster, target):
        return caster.pos.distance_to(target.pos) <= self.range

    def cast(self, action, caster, target):
        target.game_object.component(AI).confuse(self.num_turns)

    def player_cast(self, action, player, ui):
        # Ask the player for a target to confuse
        action.game.log.message('Left-click an enemy to confuse it, or right-click to cancel.',
                                libtcod.light_cyan)
        monster = pyro.utilities.target_monster(action.game, ui, self.range)
        if monster is None:
            return 'cancelled'

        self.cast(action, player, monster)
        msg = 'The eyes of the {0} look vacant as he starts to stumble around!'
        action.game.log.message(msg.format(monster.name), libtcod.light_green)
