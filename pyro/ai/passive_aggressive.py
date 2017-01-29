import libtcodpy as libtcod
from pyro.components.ai import AI
from pyro.ai.aggressive import Aggressive


class PassiveAggressive(AI):
    """Neutral, until the player attacks. May wander in a random direction."""

    def take_damage(self, damage):
        self.owner.set_component(AI, Aggressive())

    def take_turn(self):
        # 25% chance to move one square in a random direction
        if libtcod.random_get_int(0, 1, 4) == 1:
            self.owner.move(libtcod.random_get_int(0, -1, 1),
                            libtcod.random_get_int(0, -1, 1))
