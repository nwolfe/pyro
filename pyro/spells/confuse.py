import libtcodpy as libtcod
from pyro.ai.confused import Confused
from pyro.components.ai import AI
from pyro.settings import CONFUSE_RANGE
from pyro.spell import Spell


class Confuse(Spell):
    def __init__(self):
        Spell.__init__(self, 'Confusion', CONFUSE_RANGE, strength=0)

    def cast(self, caster, target):
        old_ai = target.component(AI)
        new_ai = Confused(old_ai)
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
