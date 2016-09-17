import libtcodpy as libtcod
import abilities
import math
import json
from settings import *


class Object:
    # REMIND: Consider adding the 'always_visible' property from Part 11
    def __init__(self, x=0, y=0, char=None, name=None, color=None, blocks=False,
                 render_order=1, fighter=None, ai=None, item=None, exp=None,
                 equipment=None):
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

        self.exp = exp
        if self.exp:
            self.exp.owner = self

        self.equipment = equipment
        if self.equipment:
            self.equipment.owner = self
            self.item = Item()
            self.item.owner = self

    def move(self, map, objects, dx, dy):
        if not is_blocked(map, objects, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def draw(self, console):
        # Set the color and then draw the character that
        # represents this object at its position
        libtcod.console_set_default_foreground(console, self.color)
        libtcod.console_put_char(console, self.x, self.y, self.char,
                                 libtcod.BKGND_NONE)

    def clear(self, console):
        # Erase the character that represents this object
        libtcod.console_put_char(console, self.x, self.y, ' ',
                                 libtcod.BKGND_NONE)

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


class Experience(Component):
    def __init__(self, xp=0, level=0):
        self.xp = xp
        self.level = level

    def requiredForLevelUp(self):
        return LEVEL_UP_BASE + self.level * LEVEL_UP_FACTOR

    def canLevelUp(self):
        return self.xp <= self.requiredForLevelUp()

    def levelUp(self):
        required = self.requiredForLevelUp()
        self.level += 1
        self.xp -= required


def get_equipped_in_slot(slot, game):
    for obj in game.inventory:
        item = obj.equipment
        if item and item.slot == slot and item.is_equipped:
            return item
    return None


def get_all_equipped(obj, game):
    if obj == game.player:
        equipped = []
        for item in game.inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped.append(item.equipment)
        return equipped
    else:
        return []


class Equipment(Component):
    """An object that can be equipped, yielding bonuses. Automatically adds
    the Item component."""

    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.is_equipped = False

    def toggle_equip(self, game):
        if self.is_equipped:
            self.unequip(game)
        else:
            self.equip(game)

    def equip(self, game):
        """Equip object and show a message about it."""
        replacing = get_equipped_in_slot(self.slot, game)
        if replacing is not None:
            replacing.unequip(game)
        self.is_equipped = True
        game.message('Equipped {0} on {1}.'.format(self.owner.name, self.slot),
                     libtcod.light_green)

    def unequip(self, game):
        """Unequip object and show a message about it."""
        if not self.is_equipped:
            return
        self.is_equipped = False
        game.message('Unequipped {0} from {1}.'.format(self.owner.name,
                                                       self.slot),
                     libtcod.light_yellow)


class Fighter(Component):
    """Combat-related properties and methods (monster, player, NPC)."""
    def __init__(self, hp, defense, power, death_fn=None):
        self.hp = hp
        self.base_max_hp = hp
        self.base_defense = defense
        self.base_power = power
        self.death_fn = death_fn

    def power(self, game):
        equipped = get_all_equipped(self.owner, game)
        bonus = sum(equipment.power_bonus for equipment in equipped)
        return self.base_power + bonus

    def defense(self, game):
        equipped = get_all_equipped(self.owner, game)
        bonus = sum(equipment.defense_bonus for equipment in equipped)
        return self.base_defense + bonus

    def max_hp(self, game):
        equipped = get_all_equipped(self.owner, game)
        bonus = sum(equipment.max_hp_bonus for equipment in equipped)
        return self.base_max_hp + bonus

    def take_damage(self, damage, game):
        if damage > 0:
            self.hp -= damage

        # Check for death and call the death function if there is one
        if self.hp <= 0 and self.death_fn:
            self.death_fn(self.owner, game)

    def heal(self, amount, game):
        # Heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp(game):
            self.hp = self.max_hp(game)

    def attack(self, target, game):
        damage = self.power(game) - target.fighter.defense(game)

        if damage > 0:
            game.message('{0} attacks {1} for {2} hit points.'.format(
                self.owner.name.capitalize(), target.name, damage))
            target.fighter.take_damage(damage, game)
        else:
            game.message('{0} attacks {1} but it has no effect!'.format(
                self.owner.name.capitalize(), target.name))


class AI(Component):
    def take_turn(self, game):
        # Children must implement
        return


class BasicMonster(AI):
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


class ConfusedMonster(AI):
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


def monster_death(monster, game):
    # Transform it into a nasty corpse!
    # It doesn't block, can't be attacked, and doesn't move
    game.message('The {0} is dead! You gain {1} experience points.'.
                 format(monster.name.capitalize(), monster.exp.xp),
                 libtcod.orange)
    game.player.exp.xp += monster.exp.xp
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.render_order = 0
    monster.name = 'remains of {0}'.format(monster.name)


def instantiate_monster(template):
    name = template['name']
    char = template['symbol']
    color = getattr(libtcod, template['color'])
    ai_comp = BasicMonster()
    exp_comp = Experience(template['experience'])
    fighter_comp = Fighter(template['hp'], template['defense'],
                           template['power'], death_fn=monster_death)
    return Object(char=char, name=name, color=color, blocks=True,
                  fighter=fighter_comp, ai=ai_comp, exp=exp_comp)


def make_monster(name, monster_templates):
    for template in monster_templates:
        if template['name'] == name:
            return instantiate_monster(template)


def load_templates(file):
    with open(file) as f:
        templates = json.load(f)

        # For some reason the UI renderer can't handle Unicode strings so we
        # need to convert the character symbol to UTF-8 for it to be rendered
        for t in templates:
            t['symbol'] = str(t['symbol'])

        return templates


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
            # Special case: automatically equip if slot is empty
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot, game) is None:
                equipment.equip(game)

    def drop(self, game):
        # Remove from the inventory and add to the map.
        # Place at player's coordinates.
        game.inventory.remove(self.owner)
        game.objects.append(self.owner)
        self.owner.x = game.player.x
        self.owner.y = game.player.y
        # Special case: unequip before dropping
        if self.owner.equipment:
            self.owner.equipment.unequip(game)
        game.message('You dropped a {0}.'.format(self.owner.name),
                     libtcod.yellow)

    def use(self, game, console, panel):
        # Call the use_fn if we have one
        if self.owner.equipment:
            # Special case: the "use" action is to equip/unequip
            self.owner.equipment.toggle_equip(game)
        elif self.use_fn is None:
            game.message('The {0} cannot be used.'.format(self.owner.name))
        else:
            # Destroy after use, unless it was cancelled for some reason
            result = self.use_fn(self.item_owner, game, console, panel)
            if result != 'cancelled':
                game.inventory.remove(self.owner)


def instantiate_item(template):
    name = template['name']
    char = template['symbol']
    color = getattr(libtcod, template['color'])
    if 'slot' in template:
        equipment = Equipment(slot=template['slot'])
        if 'power' in template:
            equipment.power_bonus = template['power']
        if 'defense' in template:
            equipment.defense_bonus = template['defense']
        if 'hp' in template:
            equipment.max_hp_bonus = template['hp']
        return Object(char=char, name=name, color=color, render_order=0,
                      equipment=equipment)
    elif 'on_use' in template:
        use_fn = getattr(abilities, template['on_use'])
        return Object(char=char, name=name, color=color, render_order=0,
                      item=Item(use_fn=use_fn))


def make_item(name, item_templates):
    for template in item_templates:
        if template['name'] == name:
            return instantiate_item(template)
