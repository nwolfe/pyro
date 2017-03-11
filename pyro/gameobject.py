import math
import tcod as libtcod
from pyro.events import EventSource
from pyro.settings import RENDER_ORDER_DEFAULT


class GameObject(EventSource):
    def __init__(self, x=0, y=0, glyph=None, name=None, color=None, blocks=False,
                 render_order=RENDER_ORDER_DEFAULT, always_visible=False, components=None,
                 game=None, listeners=None):
        EventSource.__init__(self, listeners)
        self.x = x
        self.y = y
        self.glyph = glyph
        self.color = color
        self.name = name
        self.render_order = render_order
        self.always_visible = always_visible
        self.blocks = blocks
        self.game = game

        self.components = {}
        if components:
            for comp in components:
                self.set_component(comp)

    def component(self, component_type):
        return self.components.get(component_type)

    def set_component(self, component):
        self.remove_component(component.type)
        self.components[component.type] = component
        component.set_owner(self)

    def remove_component(self, component_type):
        if component_type in self.components:
            self.components.pop(component_type).remove_owner(self)

    def add_to_game(self):
        self.game.add_object(self)

    def remove_from_game(self):
        self.game.remove_object(self)

    def move(self, dx, dy):
        if not self.game.is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        else:
            return False

    def draw(self, console):
        always_visible = self.always_visible and self.game.game_map.is_explored(self.x, self.y)
        if always_visible or self.game.game_map.is_in_fov(self.x, self.y):
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

    def move_astar(self, x, y, passthrough=False):
        # Create a FOV map that has the dimensions of the map
        fov = self.game.game_map.make_fov_map()

        # Scan all the objects to see if there are objects that must be
        # navigated around. Check also that the object isn't self or the
        # target (so that the start and the end points are free).
        # The AI class handles the situation if self is next to the target so
        # it will not use this A* function anyway.
        # Things like projectiles should just "pass through" objects rather
        # than fly around them.
        if not passthrough:
            for obj in self.game.objects:
                if obj.blocks and obj != self and obj.x != x and obj.y != y:
                    # Set the tile as a wall so it must be navigated around
                    libtcod.map_set_properties(fov, obj.x, obj.y, isTrans=True, isWalk=False)

        # Allocate an A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0
        # if diagonal moves are prohibited
        path = libtcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(path, self.x, self.y, x, y)

        # Check if the path exists, and in this case, also the path is shorter
        # than 25 tiles. The path size matters if you want the monster to use
        # alternative longer paths (for example through other rooms). It makes
        # sense to keep path size relatively low to keep the monsters from
        # running around the map if there's an alternative path really far away
        if not libtcod.path_is_empty(path) and libtcod.path_size(path) < 25:
            # Find the next coordinates in the computed full path
            next_x, next_y = libtcod.path_walk(path, True)
            if next_x or next_y:
                # Set self's coordinates to the next path tile
                self.x = next_x
                self.y = next_y
        else:
            # Keep the old move function as a backup so that if there are no
            # paths (for example, another monster blocks a corridor). It will
            # still try to move towards the player (closer to the corridor opening)
            self.move_towards(x, y)

        # Delete the path to free memory
        libtcod.path_delete(path)
