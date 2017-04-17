import tcod as libtcod
import pyro.direction
from pyro.components import AI
from pyro.settings import SPELL_CONFUSE_TURNS
from pyro.engine.actions import WalkAction
from pyro.utilities import blocked


class Confused(AI):
    """Wanders in a random direction for the specified number of turns, then
    sets the owner's AI to the specified implementation."""

    def __init__(self, restore_ai=None, num_turns=SPELL_CONFUSE_TURNS):
        AI.__init__(self)
        self.restore_ai = restore_ai
        self.num_turns = num_turns

    def take_turn(self, action):
        if self.restore_ai is None or self.num_turns > 0:
            self.num_turns -= 1
            # Move in a random direction
            direction = pyro.direction.random()
            if not blocked(self.owner.game, self.owner.pos.plus(direction)):
                return WalkAction(direction)
        else:
            # Restore normal AI
            self.owner.set_component(self.restore_ai)
            msg = 'The {0} is no longer confused!'.format(self.owner.name)
            self.owner.game.message(msg, libtcod.red)
