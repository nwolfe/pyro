import libtcodpy as libtcod
import pyro.component as libcomp


class Spellcaster(libcomp.Component):
    def __init__(self, spell):
        self.spell = spell

    def in_range(self, target):
        return self.owner.distance_to(target) <= self.spell.range()

    def cast_spell(self, targets):
        # Only 40% chance to hit
        if libtcod.random_get_int(0, 1, 5) <= 2:
            self.spell.cast(self.owner, targets)
            msg = 'The {0} strikes you with a {1}! You take {2} damage.'
            msg = msg.format(self.owner.name, self.spell.name, self.spell.strength())
            self.owner.game.message(msg, libtcod.red)
        else:
            msg = 'The {0} casts a {1} but it fizzles!'
            msg = msg.format(self.owner.name, self.spell.name)
            self.owner.game.message(msg)
