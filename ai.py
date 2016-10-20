import libtcodpy as libtcod
import component as libcomp
import fighter as libfighter
import abilities as libabil
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
        if libtcod.map_is_in_fov(monster.game.fov_map, monster.x, monster.y):
            # Move towards player if far away
            if monster.distance_to(monster.game.player) >= 2:
                monster.move_astar(monster.game.player)

            # Close enough, attack! (If the player is still alive)
            elif monster.game.player.component(libfighter.Fighter).hp > 0:
                monster.component(libfighter.Fighter).attack(monster.game.player)


class AggressiveSpellcaster(AI):
    def take_turn(self):
        monster = self.owner
        player = monster.game.player
        if libtcod.map_is_in_fov(monster.game.fov_map, monster.x, monster.y):
            # Move towards player if far away
            if monster.distance_to(player) >= LIGHTNING_RANGE:
                monster.move_astar(player)

            # Close enough, attack! (If the player is still alive)
            elif player.component(libfighter.Fighter).hp > 0:
                # 50% chance to hit
                if libtcod.random_get_int(0, 0, 1) == 0:
                    libabil.monster_cast_lightning(monster, player,
                                                   LIGHTNING_DAMAGE / 3,
                                                   monster.game)


class PassiveAggressive(AI):
    """Neutral, until the player attacks. May wander in a random direction."""

    def take_damage(self, damage):
        self.owner.set_component(AI, Aggressive())

    def take_turn(self):
        # 25% chance to move one square in a random direction
        if libtcod.random_get_int(0, 1, 4) == 1:
            self.owner.move(libtcod.random_get_int(0, -1, 1),
                            libtcod.random_get_int(0, -1, 1))


class Confused(AI):
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
            self.owner.set_component(AI, self.restore_ai)
            msg = 'The {0} is no longer confused!'.format(self.owner.name)
            self.owner.game.message(msg, libtcod.red)


def aggressive():
    return Aggressive()


def aggressive_spellcaster():
    return AggressiveSpellcaster()


def passive_aggressive():
    return PassiveAggressive()


def confused():
    return Confused()
