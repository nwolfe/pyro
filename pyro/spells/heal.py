import libtcodpy as libtcod
from pyro.components import Fighter
from pyro.spell import Spell
from pyro.settings import SPELL_HEAL_STRENGTH


class Heal(Spell):
    def __init__(self):
        Spell.__init__(self, 'Healing')
        self.strength = SPELL_HEAL_STRENGTH

    def configure(self, settings):
        self.strength = settings.get('strength', self.strength)

    def in_range(self, caster, target):
        return caster == target

    def cast(self, caster, target):
        target.component(Fighter).heal(self.strength)

    def player_cast(self, player, game, ui):
        # Heal the player
        fighter = player.component(Fighter)
        if fighter.hp == fighter.max_hp():
            game.message('You are already at full health.', libtcod.red)
            return 'cancelled'

        game.message('Your wounds start to feel better!', libtcod.light_violet)
        self.cast(player, player)
