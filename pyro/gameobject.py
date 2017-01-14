import math
import libtcodpy as libtcod
import pyro.utilities as libutils
from pyro.settings import *


class GameObject:
    def __init__(self, x=0, y=0, glyph=None, name=None, color=None, blocks=False,
                 render_order=1, always_visible=False, components=None, game=None):
        self.x = x
        self.y = y
        self.glyph = glyph
        self.color = color
        self.name = name
        self.render_order = render_order
        self.always_visible = always_visible
        self.blocks = blocks
        self.game = game

        if components:
            self.components = components
            for comp in self.components.values():
                comp.initialize(self)
        else:
            self.components = {}

    def component(self, klass):
        return self.components.get(klass)

    def set_component(self, klass, comp):
        self.components[klass] = comp
        comp.initialize(self)

    def move(self, dx, dy):
        if not libutils.is_blocked(self.game.map, self.game.objects,
                                   self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        else:
            return False

    def draw(self, console, map, fov_map):
        always_visible = self.always_visible and map[self.x][self.y].explored
        if always_visible or libtcod.map_is_in_fov(fov_map, self.x, self.y):
            # Set the color and then draw the character that
            # represents this object at its position
            libtcod.console_set_default_foreground(console, self.color)
            libtcod.console_put_char(console, self.x, self.y, self.glyph,
                                     libtcod.BKGND_NONE)

    def clear(self, console):
        # Erase the character that represents this object
        libtcod.console_put_char(console, self.x, self.y, ' ',
                                 libtcod.BKGND_NONE)

    def move_towards(self, target_x, target_y):
        # Vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move_astar(self, target):
        # Create a FOV map that has the dimensions of the map
        fov = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)

        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(MAP_HEIGHT):
            for x1 in range(MAP_WIDTH):
                libtcod.map_set_properties(fov, x1, y1,
                                           not self.game.map[x1][y1].block_sight,
                                           not self.game.map[x1][y1].blocked)

        # Scan all the objects to see if there are objects that must be
        # navigated around. Check also that the object isn't self or the
        # target (so that the start and the end points are free).
        # The AI class handles the situation if self is next to the target so
        # it will not use this A* function anyway.
        for obj in self.game.objects:
            if obj.blocks and obj != self and obj != target:
                # Set the tile as a wall so it must be navigated around
                libtcod.map_set_properties(fov, obj.x, obj.y, True, False)

        # Allocate an A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0
        # if diagonal moves are prohibited
        path = libtcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter
        # than 25 tiles. The path size matters if you want the monster to use
        # alternative longer paths (for example through other rooms). It makes
        # sense to keep path size relatively low to keep the monsters from
        # running around the map if there's an alternative path really far away
        if not libtcod.path_is_empty(path) and libtcod.path_size(path) < 25:
            # Find the next coordinates in the computed full path
            x, y = libtcod.path_walk(path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no
            # paths (for example, another monster blocks a corridor). It will
            # still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y)

        # Delete the path to free memory
        libtcod.path_delete(path)
