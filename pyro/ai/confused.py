import libtcodpy as libtcod
import components.ai as libai
from settings import *


class Confused(libai.AI):
    """Wanders in a random direction for the specified number of turns, then
    sets the owner's AI to the specified implementation."""

    def __init__(self, restore_ai=None, num_turns=CONFUSE_NUM_TURNS):
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
            self.owner.set_component(libai.AI, self.restore_ai)
            msg = 'The {0} is no longer confused!'.format(self.owner.name)
            self.owner.game.message(msg, libtcod.red)
