import tcod as libtcod
from pyro.component import Component
from pyro.spell import SpellType


class Spellcaster(Component):
    def __init__(self, spells):
        Component.__init__(self, component_type=Spellcaster)
        self.spells = {SpellType.ATTACK: [], SpellType.HEAL: []}
        for spell in spells:
            self.spells[spell.type].append(spell)

    def get_spells(self, spell_type):
        return self.spells[spell_type]

    def in_range(self, target, spell_type):
        for spell in self.spells[spell_type]:
            if spell.in_range(self.owner, target):
                return True
        return False

    def cast_spell(self, spell, target):
        if SpellType.ATTACK == spell.type:
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
        elif SpellType.HEAL == spell.type:
            spell.cast(self.owner, target)
            msg = 'The {0} heals itself!'.format(self.owner.name)
            self.owner.game.message(msg)
