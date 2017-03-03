import libtcodpy as libtcod
from pyro.ai import Confused
from pyro.components import AI
from pyro.spell import Spell
from pyro.settings import SPELL_CONFUSE_RANGE, SPELL_CONFUSE_TURNS


class Confuse(Spell):
    def __init__(self):
        Spell.__init__(self, 'Confusion')
        self.range = SPELL_CONFUSE_RANGE
        self.num_turns = SPELL_CONFUSE_TURNS

    def configure(self, settings):
        self.range = settings.get('range', self.range)
        self.num_turns = settings.get('turns', self.num_turns)

    def in_range(self, caster, target):
        return caster.distance_to(target) <= self.range

    def cast(self, caster, target):
        old_ai = target.component(AI)
        new_ai = Confused(restore_ai=old_ai, num_turns=self.num_turns)
        target.set_component(new_ai)

    def player_cast(self, player, game, ui):
        # Ask the player for a target to confuse
        game.message('Left-click an enemy to confuse it, or right-click to cancel.',
                     libtcod.light_cyan)
        monster = game.target_monster(ui, self.range)
        if monster is None:
            return 'cancelled'

        self.cast(player, monster)
        msg = 'The eyes of the {0} look vacant as he starts to stumble around!'
        game.message(msg.format(monster.name), libtcod.light_green)
