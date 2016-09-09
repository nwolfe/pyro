import libtcodpy as libtcod
import object as libobj
from settings import *


def cast_heal(player, game):
    # Heal the player
    if game.player.fighter.hp == game.player.fighter.max_hp:
        game.message('You are already at full health.', libtcod.red)
        return 'cancelled'

    game.message('Your wounds start to feel better!',
                 libtcod.light_violet)
    game.player.fighter.heal(HEAL_AMOUNT)


def cast_lightning(player, game):
    # Find the closest enemy (inside a maximum range) and damage it
    monster = libobj.closest_monster(LIGHTNING_RANGE, game)
    if monster is None:
        game.message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'

    # Zap it!
    msg = 'A lightning bolt strikes the {0} with a loud thunderclap! '
    msg += 'The damage is {1} hit points.'
    msg = msg.format(monster.name, LIGHTNING_DAMAGE)
    game.message(msg, libtcod.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE, game)


def cast_confuse(player, game):
    # Ask the player for a target to confuse
    game.message('Left-click an enemy to confuse it, or right-click to cancel.',
                 libtcod.light_cyan)
    monster = game.target_monster(CONFUSE_RANGE)
    if monster is None:
        return 'cancelled'

    old_ai = monster.ai
    monster.ai = libobj.ConfusedMonster(old_ai)
    monster.ai.owner = monster
    msg = 'The eyes of the {0} look vacant as he starts to stumble around!'
    game.message(msg.format(monster.name), libtcod.light_green)


def cast_fireball(player, game):
    # Ask the player for a target tile to throw a fireball at
    msg = 'Left-click a target tile for the fireball, or right-click to cancel.'
    game.message(msg, libtcod.light_cyan)
    (x, y) = game.target_tile()
    if x is None:
        return 'cancelled'

    game.message('The fireball explodes, burning everything within {0} tiles!'.
                 format(FIREBALL_RADIUS), libtcod.orange)

    for object in game.objects:
        if object.distance(x, y) <= FIREBALL_RADIUS and object.fighter:
            game.message('The {0} gets burned for {1} hit points.'.format(
                object.name, FIREBALL_DAMAGE), libtcod.orange)
            object.fighter.take_damage(FIREBALL_DAMAGE, game)