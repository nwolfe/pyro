import tcod as libtcod
from random import shuffle
from pyro.component import Component


class Spellcaster(Component):
    def __init__(self, spells):
        Component.__init__(self, component_type=Spellcaster)
        self.spells = spells

    def in_range(self, target):
        for spell in self.spells:
            if spell.in_range(self.owner, target):
                return True
        return False

    def cast_spell(self, target):
        spell = self.choose_spell(target)
        if spell is None:
            return

        # Only 40% chance to hit
        if libtcod.random_get_int(0, 1, 5) <= 2:
            damage = spell.cast(self.owner, target)
            msg = 'The {0} strikes you with a {1}! You take {2} damage.'
            msg = msg.format(self.owner.name, spell.name, damage)
            self.owner.game.message('- ' + msg, libtcod.red)
        else:
            msg = 'The {0} casts a {1} but it fizzles!'
            msg = msg.format(self.owner.name, spell.name)
            self.owner.game.message(msg)

    def choose_spell(self, target):
        # Randomly pick spells and return the first that's in range
        shuffle(self.spells)
        for spell in self.spells:
            if spell.in_range(self.owner, target):
                return spell
        return None
