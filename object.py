import libtcodpy as libtcod
import math
from settings import *


def is_blocked(map, objects, x, y):
    # First test the map tile
    if map[x][y].blocked:
        return True

    # Now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False


def closest_monster(max_range, game):
    # Find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1

    for object in game.objects:
        if object.fighter and object != game.player and libtcod.map_is_in_fov(
                game.fov_map, object.x, object.y):
            # Calculate distance between this object and the player
            dist = game.player.distance_to(object)
            if dist < closest_dist:
                closest_dist = dist
                closest_enemy = object

    return closest_enemy


class Object:
    # REMIND: Consider adding the 'always_visible' property from Part 11
    def __init__(self, x, y, char, name, color, blocks=False, render_order=1,
                 fighter=None, ai=None, item=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.render_order = render_order
        self.blocks = blocks
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai.owner = self
        self.item = item
        if self.item:
            self.item.owner = self

    def move(self, map, objects, dx, dy):
        if not is_blocked(map, objects, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def draw(self, con):
        # Set the color and then draw the character that
        # represents this object at its position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char,
                                 libtcod.BKGND_NONE)

    def clear(self, con):
        # Erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def move_towards(self, map, objects, target_x, target_y):
        # Vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(map, objects, dx, dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)


class Component:
    def __init__(self):
        self.owner = None


class Fighter(Component):
    """Combat-related properties and methods (monster, player, NPC)."""
    def __init__(self, hp, defense, power, death_fn=None):
        self.hp = hp
        self.max_hp = hp
        self.defense = defense
        self.power = power
        self.death_fn = death_fn

    def take_damage(self, damage, game):
        if damage > 0:
            self.hp -= damage

        # Check for death and call the death function if there is one
        if self.hp <= 0 and self.death_fn:
            self.death_fn(self.owner, game)

    def heal(self, amount):
        # Heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target, game):
        damage = self.power - target.fighter.defense

        if damage > 0:
            game.message('{0} attacks {1} for {2} hit points.'.format(
                self.owner.name.capitalize(), target.name, damage))
            target.fighter.take_damage(damage, game)
        else:
            game.message('{0} attacks {1} but it has no effect!'.format(
                self.owner.name.capitalize(), target.name))


class AI:
    def take_turn(self, game):
        # Children must implement
        return


class BasicMonster(Component, AI):
    def take_turn(self, game):
        monster = self.owner
        if libtcod.map_is_in_fov(game.fov_map, monster.x, monster.y):
            # Move towards player if far away
            if monster.distance_to(game.player) >= 2:
                monster.move_towards(game.map, game.objects,
                                     game.player.x, game.player.y)

            # Close enough, attack! (If the player is still alive)
            elif game.player.fighter.hp > 0:
                monster.fighter.attack(game.player, game)


class ConfusedMonster(Component, AI):
    def __init__(self, restore_ai, num_turns=CONFUSE_NUM_TURNS):
        self.restore_ai = restore_ai
        self.num_turns = num_turns

    def take_turn(self, game):
        if self.num_turns > 0:
            # Move in a random direction
            self.owner.move(game.map, game.objects,
                            libtcod.random_get_int(0, -1, 1),
                            libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:
            # Restore normal AI
            self.owner.ai = self.restore_ai
            msg = 'The {0} is no longer confused!'.format(self.owner.name)
            game.message(msg, libtcod.red)


def monster_death(monster, game):
    # Transform it into a nasty corpse!
    # It doesn't block, can't be attacked, and doesn't move
    game.message('{0} is dead!'.format(monster.name.capitalize()))
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.render_order = 0
    monster.name = 'remains of {0}'.format(monster.name)


def make_orc(x, y):
    ai_comp = BasicMonster()
    fighter_comp = Fighter(hp=10, defense=0, power=3, death_fn=monster_death)
    return Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True,
                  ai=ai_comp, fighter=fighter_comp)


def make_troll(x, y):
    ai_comp = BasicMonster()
    fighter_comp = Fighter(hp=16, defense=1, power=4, death_fn=monster_death)
    return Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True,
                  ai=ai_comp, fighter=fighter_comp)


class Item(Component):
    def __init__(self, use_fn=None):
        self.use_fn = use_fn
        self.item_owner = None

    def pick_up(self, game):
        # Add to player's inventory and remove from the map
        if len(game.inventory) >= 26:
            game.message('Your inventory is full, cannot pick up {0}.'.format(
                self.owner.name), libtcod.red)
        else:
            self.item_owner = game.player
            game.inventory.append(self.owner)
            game.objects.remove(self.owner)
            game.message('You picked up a {0}!'.format(self.owner.name),
                         libtcod.green)

    def drop(self, game):
        # Remove from the inventory and add to the map.
        # Place at player's coordinates.
        game.inventory.remove(self.owner)
        game.objects.append(self.owner)
        self.owner.x = game.player.x
        self.owner.y = game.player.y
        game.message('You dropped a {0}.'.format(self.owner.name),
                     libtcod.yellow)

    def use(self, game):
        # Call the use_fn if we have one
        if self.use_fn is None:
            game.message('The {0} cannot be used.'.format(self.owner.name))
        else:
            # Destroy after use, unless it was cancelled for some reason
            if self.use_fn(self.item_owner, game) != 'cancelled':
                game.inventory.remove(self.owner)


def cast_heal(player, game):
    # Heal the player
    if game.player.fighter.hp == game.player.fighter.max_hp:
        game.message('You are already at full health.', libtcod.red)
        return 'cancelled'

    game.message('Your wounds start to feel better!',
                 libtcod.light_violet)
    game.player.fighter.heal(HEAL_AMOUNT)


def make_healing_potion(x, y):
    item_comp = Item(use_fn=cast_heal)
    return Object(x, y, '!', 'healing potion', libtcod.violet,
                  render_order=0, item=item_comp)


def cast_lightning(player, game):
    # Find the closest enemy (inside a maximum range) and damage it
    monster = closest_monster(LIGHTNING_RANGE, game)
    if monster is None:
        game.message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'

    # Zap it!
    msg = 'A lightning bolt strikes the {0} with a loud thunderclap! '
    msg += 'The damage is {1} hit points.'
    msg = msg.format(monster.name, LIGHTNING_DAMAGE)
    game.message(msg, libtcod.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE, game)


def make_lightning_scroll(x, y):
    item_comp = Item(use_fn=cast_lightning)
    return Object(x, y, '#', 'scroll of lightning bolt',
                  libtcod.light_yellow, render_order=0, item=item_comp)


def cast_confuse(player, game):
    # Ask the player for a target to confuse
    game.message('Left-click an enemy to confuse it, or right-click to cancel.',
                 libtcod.light_cyan)
    monster = game.target_monster(CONFUSE_RANGE)
    if monster is None:
        return 'cancelled'

    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster
    msg = 'The eyes of the {0} look vacant as he starts to stumble around!'
    game.message(msg.format(monster.name), libtcod.light_green)


def make_confusion_scroll(x, y):
    item_comp = Item(use_fn=cast_confuse)
    return Object(x, y, '#', 'scroll of confusion',
                  libtcod.light_yellow, render_order=0, item=item_comp)


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


def make_fireball_scroll(x, y):
    item_comp = Item(use_fn=cast_fireball)
    return Object(x, y, '#', 'scroll of fireball',
                  libtcod.light_yellow, render_order=0, item=item_comp)
