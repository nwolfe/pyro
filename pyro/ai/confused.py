import libtcodpy as libtcod
from pyro.components.ai import AI
from pyro.settings import *


class Confused(AI):
    """Wanders in a random direction for the specified number of turns, then
    sets the owner's AI to the specified implementation."""

    def __init__(self, restore_ai=None, num_turns=CONFUSE_NUM_TURNS):
        AI.__init__(self)
        self.restore_ai = restore_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.restore_ai is None or self.num_turns > 0:
            # Move in a random direction
            self.owner.move(libtcod.random_get_int(0, -1, 1),
                            libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:
            # Restore normal AI
            self.owner.set_component(AI, self.restore_ai)
            msg = 'The {0} is no longer confused!'.format(self.owner.name)
            self.owner.game.message(msg, libtcod.red)
