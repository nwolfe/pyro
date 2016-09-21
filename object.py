import libtcodpy as libtcod
import ai as libai
import item as libitem
import experience as libxp
import fighter as libfighter
import abilities
import math
import json
from settings import *


class Object:
    def __init__(self, x=0, y=0, char=None, name=None, color=None, blocks=False,
                 render_order=1, always_visible=False, components={}):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.render_order = render_order
        self.always_visible = always_visible
        self.blocks = blocks

        self.components = components
        for component in self.components.values():
            component.initialize(self)

    def move(self, map, objects, dx, dy):
        if not is_blocked(map, objects, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def draw(self, console, map, fov_map):
        always_visible = self.always_visible and map[self.x][self.y].explored
        if always_visible or libtcod.map_is_in_fov(fov_map, self.x, self.y):
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


def is_blocked(map, objects, x, y):
    # First test the map tile
    if map[x][y].blocked:
        return True

    # Now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False


def monster_death(monster, game):
    # Transform it into a nasty corpse!
    # It doesn't block, can't be attacked, and doesn't move
    exp = monster.components.get(libxp.Experience)
    game.message('The {0} is dead! You gain {1} experience points.'.
                 format(monster.name.capitalize(), exp.xp),
                 libtcod.orange)
    game.player.components.get(libxp.Experience).xp += exp.xp
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.render_order = 0
    monster.name = 'remains of {0}'.format(monster.name)
    monster.components.pop(libfighter.Fighter)
    monster.components.pop(libai.AI)


def instantiate_monster(template):
    name = template['name']
    char = template['symbol']
    color = getattr(libtcod, template['color'])
    ai_comp_fn = getattr(libai, template['ai'])
    ai_comp = ai_comp_fn()
    exp_comp = libxp.Experience(template['experience'])
    fighter_comp = libfighter.Fighter(template['hp'], template['defense'],
                                   template['power'], death_fn=monster_death)
    return Object(char=char, name=name, color=color, blocks=True,
                  components={libfighter.Fighter: fighter_comp,
                              libai.AI: ai_comp,
                              libxp.Experience: exp_comp})


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


def instantiate_item(template):
    name = template['name']
    char = template['symbol']
    color = getattr(libtcod, template['color'])
    if 'slot' in template:
        equipment = libitem.Equipment(slot=template['slot'])
        if 'power' in template:
            equipment.power_bonus = template['power']
        if 'defense' in template:
            equipment.defense_bonus = template['defense']
        if 'hp' in template:
            equipment.max_hp_bonus = template['hp']
        return Object(char=char, name=name, color=color, render_order=0,
                      components={libitem.Equipment: equipment})
    elif 'on_use' in template:
        use_fn = getattr(abilities, template['on_use'])
        return Object(char=char, name=name, color=color, render_order=0,
                      components={libitem.Item: libitem.Item(use_fn=use_fn)})


def make_item(name, item_templates):
    for template in item_templates:
        if template['name'] == name:
            return instantiate_item(template)
