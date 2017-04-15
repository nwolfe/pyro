import tcod as libtcod
import pyro.direction
from pyro.components import AI, Fighter
from pyro.ai import Aggressive


class PassiveAggressive(AI):
    """Neutral, until the player attacks. May wander in a random direction."""
    def take_turn(self, action):
        # Become aggressive if we're damaged
        fighter = self.owner.component(Fighter)
        if fighter and fighter.hp < fighter.max_hp():
            self.owner.set_component(Aggressive())

        # 25% chance to move one square in a random direction
        elif libtcod.random_get_int(0, 1, 4) == 1:
            self.move(pyro.direction.random())
