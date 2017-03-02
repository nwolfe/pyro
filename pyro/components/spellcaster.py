import libtcodpy as libtcod
from pyro.component import Component


class Spellcaster(Component):
    def __init__(self, spell):
        Component.__init__(self, component_type=Spellcaster)
        self.spell = spell

    def in_range(self, target):
        return self.spell.in_range(self.owner, target)

    def cast_spell(self, target):
        # Only 40% chance to hit
        if libtcod.random_get_int(0, 1, 5) <= 2:
            damage = self.spell.cast(self.owner, target)
            msg = 'The {0} strikes you with a {1}! You take {2} damage.'
            msg = msg.format(self.owner.name, self.spell.name, damage)
            self.owner.game.message('- ' + msg, libtcod.red)
        else:
            msg = 'The {0} casts a {1} but it fizzles!'
            msg = msg.format(self.owner.name, self.spell.name)
            self.owner.game.message(msg)
