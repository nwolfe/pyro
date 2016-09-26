import libtcodpy as libtcod
import component as libcomp
import fighter as libfighter
from settings import *


class AI(libcomp.Component):
    def take_turn(self, game):
        # Children must implement
        return


class Aggressive(AI):
    def take_turn(self, game):
        monster = self.owner
        if libtcod.map_is_in_fov(game.fov_map, monster.x, monster.y):
            # Move towards player if far away
            if monster.distance_to(game.player) >= 2:
                monster.move_astar(game.player, game.map, game.objects)

            # Close enough, attack! (If the player is still alive)
            elif game.player.components.get(libfighter.Fighter).hp > 0:
                monster.components.get(libfighter.Fighter).attack(game.player, game)


def basic():
    return Aggressive()


class Confused(AI):
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
            self.owner.components[AI] = self.restore_ai
            self.restore_ai.initialize(self.owner)
            msg = 'The {0} is no longer confused!'.format(self.owner.name)
            game.message(msg, libtcod.red)


def confused():
    return Confused()
