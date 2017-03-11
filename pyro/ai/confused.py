import tcod as libtcod
from pyro.components import AI, Movement
from pyro.settings import SPELL_CONFUSE_TURNS


class Confused(AI):
    """Wanders in a random direction for the specified number of turns, then
    sets the owner's AI to the specified implementation."""

    def __init__(self, restore_ai=None, num_turns=SPELL_CONFUSE_TURNS):
        AI.__init__(self)
        self.restore_ai = restore_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.restore_ai is None or self.num_turns > 0:
            # Move in a random direction
            movement = self.owner.component(Movement)
            if movement:
                movement.move(libtcod.random_get_int(0, -1, 1),
                              libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:
            # Restore normal AI
            self.owner.set_component(self.restore_ai)
            msg = 'The {0} is no longer confused!'.format(self.owner.name)
            self.owner.game.message(msg, libtcod.red)
