import tcod as libtcod
from pyro.component import Component
from pyro.spell import SpellType


class AI(Component):
    def __init__(self):
        Component.__init__(self, component_type=AI)
        self.__spells = None

    def take_turn(self, action):
        """Perform a single game turn."""
        pass

    def set_spells(self, spells):
        self.__spells = {SpellType.ATTACK: [], SpellType.HEAL: []}
        for spell in spells:
            self.__spells[spell.type].append(spell)

    def get_spells(self, spell_type):
        return self.__spells[spell_type]

    def in_range(self, target, spell_type):
        for spell in self.__spells[spell_type]:
            if spell.in_range(self.owner, target):
                return True
        return False

    def cast_spell(self, action, spell, target):
        if SpellType.ATTACK == spell.type:
            # Only 40% chance to hit
            if libtcod.random_get_int(0, 1, 5) <= 2:
                damage = spell.cast(action, self.owner.actor, target.actor)
                msg = 'The {0} strikes you with a {1}! You take {2} damage.'
                msg = msg.format(self.owner.name, spell.name, damage)
                self.owner.game.log.message('- ' + msg, libtcod.red)
            else:
                msg = 'The {0} casts a {1} but it fizzles!'
                msg = msg.format(self.owner.name, spell.name)
                self.owner.game.log.message(msg)
        elif SpellType.HEAL == spell.type:
            spell.cast(action, self.owner.actor, target.actor)
            msg = 'The {0} heals itself!'.format(self.owner.name)
            self.owner.game.log.message(msg)