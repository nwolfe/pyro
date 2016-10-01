import libtcodpy as libtcod
import component as libcomp
import fighter as libfighter
from settings import *


class AI(libcomp.Component):
    def take_turn(self):
        """Perform a single game turn."""
        return

    def take_damage(self, damage):
        """Called by the Fighter component when the owner takes damage."""
        return


class Aggressive(AI):
    """Pursue and attack the player once in sight."""

    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(self.game.fov_map, monster.x, monster.y):
            # Move towards player if far away
            if monster.distance_to(self.game.player) >= 2:
                monster.move_astar(self.game.player, self.game.map, self.game.objects)

            # Close enough, attack! (If the player is still alive)
            elif self.game.player.component(libfighter.Fighter).hp > 0:
                monster.component(libfighter.Fighter).attack(self.game.player)


def basic():
    return Aggressive()


class Passive(AI):
    """Neutral, until the player attacks. May wander in a random direction."""

    def take_damage(self, damage):
        aggressive = Aggressive()
        aggressive.game = self.game
        self.owner.set_component(AI, aggressive)

    def take_turn(self):
        # 25% chance to move one square in a random direction
        if libtcod.random_get_int(0, 1, 4) == 1:
            self.owner.move(self.game.map, self.game.objects,
                            libtcod.random_get_int(0, -1, 1),
                            libtcod.random_get_int(0, -1, 1))


def passive():
    return Passive()

class Confused(AI):
    """Wanders in a random direction for the specified number of turns, then
    sets the owner's AI to the specified implementation."""

    def __init__(self, restore_ai=None, num_turns=CONFUSE_NUM_TURNS):
        self.restore_ai = restore_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.restore_ai is None or self.num_turns > 0:
            # Move in a random direction
            self.owner.move(self.game.map, self.game.objects,
                            libtcod.random_get_int(0, -1, 1),
                            libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:
            # Restore normal AI
            self.owner.set_component(AI, self.restore_ai)
            msg = 'The {0} is no longer confused!'.format(self.owner.name)
            self.game.message(msg, libtcod.red)


def confused():
    return Confused()
