import tcod as libtcod
from pyro.spell import Spell
from pyro.settings import SPELL_HEAL_STRENGTH


class Heal(Spell):
    def __init__(self):
        Spell.__init__(self, 'Healing', Spell.TYPE_HEAL)
        self.strength = SPELL_HEAL_STRENGTH

    def configure(self, settings):
        self.strength = settings.get('strength', self.strength)

    def in_range(self, caster, target):
        return caster == target

    def cast(self, action, caster, target):
        if caster.is_player():
            if caster.hp == caster.max_hp:
                action.game.log.message('You are already at full health.', libtcod.red)
                return
            action.game.log.message('Your wounds start to feel better!', libtcod.light_violet)
            target = caster

        target.heal(self.strength)

    def requires_target(self):
        return False
