import libtcodpy as libtcod
import game as libgame
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


class Object:
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
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

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


class Component:
    def __init__(self):
        self.owner = None


class Fighter(Component):
    """Combat-related properties and methods (monster, player, NPC)."""
    def __init__(self, hp, defense, power, death_fn=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_fn = death_fn

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage

        # Check for death and call the death function if there is one
        if self.hp <= 0 and self.death_fn:
            self.death_fn(self.owner)

    def heal(self, amount):
        # Heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target, messages):
        damage = self.power - target.fighter.defense

        if damage > 0:
            libgame.message(messages, '{0} attacks {1} for {2} hit points.'.
                            format(self.owner.name.capitalize(), target.name,
                                   damage))
            target.fighter.take_damage(damage)
        else:
            libgame.message(messages, '{0} attacks {1} but it has no effect!'
                            .format(self.owner.name.capitalize(), target.name))


class BasicMonster(Component):
    def take_turn(self, map, fov_map, objects, player, messages):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            # Move towards player if far away
            if monster.distance_to(player) >= 2:
                monster.move_towards(map, objects, player.x, player.y)

            # Close enough, attack! (If the player is still alive)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player, messages)


class MonsterFactory:
    def __init__(self, messages):
        def monster_death(monster):
            # Transform it into a nasty corpse!
            # It doesn't block, can't be attacked, and doesn't move
            libgame.message(messages, '{0} is dead!'.
                            format(monster.name.capitalize()))
            monster.char = '%'
            monster.color = libtcod.dark_red
            monster.blocks = False
            monster.fighter = None
            monster.ai = None
            monster.render_order = 0
            monster.name = 'remains of {0}'.format(monster.name)
        self.monster_death = monster_death

    def make_orc(self, x, y):
        ai_comp = BasicMonster()
        fighter_comp = Fighter(hp=10, defense=0, power=3,
                               death_fn=self.monster_death)
        return Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True,
                      ai=ai_comp, fighter=fighter_comp)

    def make_troll(self, x, y):
        ai_comp = BasicMonster()
        fighter_comp = Fighter(hp=16, defense=1, power=4,
                               death_fn=self.monster_death)
        return Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True,
                      ai=ai_comp, fighter=fighter_comp)


class Item(Component):
    def __init__(self, use_fn=None):
        self.use_fn = use_fn
        self.item_owner = None

    def pick_up(self, inventory, player, objects, messages):
        # Add to player's inventory and remove from the map
        if len(inventory) >= 26:
            libgame.message(messages,
                            'Your inventory is full, cannot pick up {0}.'.
                            format(self.owner.name), libtcod.red)
        else:
            self.item_owner = player
            inventory.append(self.owner)
            objects.remove(self.owner)
            libgame.message(messages, 'You picked up a {0}!'.
                            format(self.owner.name), libtcod.green)

    def use(self, inventory, messages):
        # Call the use_fn if we have one
        if self.use_fn is None:
            libgame.message(messages, 'The {0} cannot be used.'.
                            format(self.owner.name))
        else:
            # Destroy after use, unless it was cancelled for some reason
            if self.use_fn(self.item_owner) != 'cancelled':
                inventory.remove(self.owner)


class ItemFactory:
    def __init__(self, messages):
        def cast_heal(player):
            # Heal the player
            if player.fighter.hp == player.fighter.max_hp:
                libgame.message(messages, 'You are already at full health.',
                                libtcod.red)
                return 'cancelled'

            libgame.message(messages, 'Your wounds start to feel better!',
                            libtcod.light_violet)
            player.fighter.heal(HEAL_AMOUNT)
        self.cast_heal = cast_heal


    def make_healing_potion(self, x, y):
        # Items appear below other objects
        item_comp = Item(use_fn=self.cast_heal)
        return Object(x, y, '!', 'healing potion', libtcod.violet,
                      render_order=0, item=item_comp)
