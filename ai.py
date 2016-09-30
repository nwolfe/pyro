import libtcodpy as libtcod
import component as libcomp
import fighter as libfighter
from settings import *


class AI(libcomp.Component):
    def take_turn(self, game):
        """Perform a single game turn."""
        return

    def take_damage(self, damage, game):
        """Called by the Fighter component when the owner takes damage."""
        return


class Aggressive(AI):
    """Pursue and attack the player once in sight."""

    def take_turn(self, game):
        monster = self.owner
        if libtcod.map_is_in_fov(game.fov_map, monster.x, monster.y):
            # Move towards player if far away
            if monster.distance_to(game.player) >= 2:
                monster.move_astar(game.player, game.map, game.objects)

            # Close enough, attack! (If the player is still alive)
            elif game.player.component(libfighter.Fighter).hp > 0:
                monster.component(libfighter.Fighter).attack(game.player, game)


def basic():
    return Aggressive()


class Passive(AI):
    """Neutral, until the player attacks. May wander in a random direction."""

    def take_damage(self, damage, game):
        self.owner.set_component(AI, Aggressive())

    def take_turn(self, game):
        # 25% chance to move one square in a random direction
        if libtcod.random_get_int(0, 1, 4) == 1:
            self.owner.move(game.map, game.objects,
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

    def take_turn(self, game):
        if self.restore_ai is None or self.num_turns > 0:
            # Move in a random direction
            self.owner.move(game.map, game.objects,
                            libtcod.random_get_int(0, -1, 1),
                            libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:
            # Restore normal AI
            self.owner.set_component(AI, self.restore_ai)
            msg = 'The {0} is no longer confused!'.format(self.owner.name)
            game.message(msg, libtcod.red)


def confused():
    return Confused()
