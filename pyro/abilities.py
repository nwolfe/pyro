import libtcodpy as libtcod
from pyro.components.fighter import Fighter
from pyro.spells import Heal, LightningBolt, Confuse
from pyro.settings import *


def cast_heal(player, game, ui):
    # Heal the player
    fighter = player.component(Fighter)
    if fighter.hp == fighter.max_hp():
        game.message('You are already at full health.', libtcod.red)
        return 'cancelled'

    game.message('Your wounds start to feel better!', libtcod.light_violet)
    Heal().cast(player, player)


def cast_lightning_bolt(player, game, ui):
    # Find the closest enemy (inside a maximum range) and damage it
    spell = LightningBolt()
    monster = game.closest_monster(spell.range())
    if monster is None:
        game.message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'

    # Zap it!
    msg = 'A lightning bolt strikes the {0} with a loud thunderclap! '
    msg += 'The damage is {1} hit points.'
    msg = msg.format(monster.name, spell.strength())
    game.message(msg, libtcod.light_blue)
    spell.cast(player, monster)


def cast_confuse(player, game, ui):
    # Ask the player for a target to confuse
    spell = Confuse()
    game.message('Left-click an enemy to confuse it, or right-click to cancel.',
                 libtcod.light_cyan)
    monster = game.target_monster(ui, spell.range())
    if monster is None:
        return 'cancelled'

    spell.cast(player, monster)
    msg = 'The eyes of the {0} look vacant as he starts to stumble around!'
    game.message(msg.format(monster.name), libtcod.light_green)


def cast_fireball(player, game, ui):
    # Ask the player for a target tile to throw a fireball at
    msg = 'Left-click a target tile for the fireball, or right-click to cancel.'
    game.message(msg, libtcod.light_cyan)
    (x, y) = game.target_tile(ui)
    if x is None:
        return 'cancelled'

    game.message('The fireball explodes, burning everything within {0} tiles!'.
                 format(FIREBALL_RADIUS), libtcod.orange)

    for game_object in game.objects:
        if game_object.distance(x, y) <= FIREBALL_RADIUS:
            fighter = game_object.component(Fighter)
            if fighter:
                game.message('The {0} gets burned for {1} hit points.'.format(
                    game_object.name, FIREBALL_DAMAGE), libtcod.orange)
                fighter.take_damage(FIREBALL_DAMAGE)
