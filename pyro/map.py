import tcod as libtcod
from pyro.objects import FACTORY
from pyro.engine.game import Stage
from pyro.utilities import is_blocked
from pyro.settings import ROOM_MIN_SIZE, ROOM_MAX_SIZE, MAP_HEIGHT, MAP_WIDTH, MAX_ROOMS
from pyro.settings import COLOR_LIGHT_GROUND, COLOR_DARK_GROUND, COLOR_LIGHT_WALL, COLOR_DARK_WALL, COLOR_LIGHT_GRASS
from pyro.settings import TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGORITHM
from pyro.engine.glyph import Glyph
from pyro.position import Position


class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        return Position((self.x1 + self.x2) / 2,
                        (self.y1 + self.y2) / 2)

    def intersect(self, other):
        # Returns true if this rectangle intersects with the other one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def random_point_inside(self):
        return Position(libtcod.random_get_int(0, self.x1+1, self.x2-1),
                        libtcod.random_get_int(0, self.y1+1, self.y2-1))


class Appearance:
    def __init__(self, lit_glyph, unlit_glyph):
        self.lit = lit_glyph
        self.unlit = unlit_glyph


class TileType:
    FLOOR = None
    WALL = None
    STAIRS = None
    TALL_GRASS = None
    CRUSHED_GRASS = None
    OPEN_DOOR = None
    CLOSED_DOOR = None
    def __init__(self, appearance, passable, transparent, is_exit=False, always_visible=False):
        self.appearance = appearance
        self.passable = passable
        self.transparent = transparent
        self.is_exit = is_exit
        self.always_visible = always_visible
        self.opens_to = None
        self.closes_to = None
        self.steps_to = None


# A passable, transparent tile
def open_tile(lit, unlit):
    return TileType(Appearance(lit, unlit), passable=True, transparent=True)


# An impassable, opaque tile
def solid_tile(lit, unlit):
    return TileType(Appearance(lit, unlit), passable=False, transparent=False)


# A passable, opaque tile
def fog_tile(lit, unlit):
    return TileType(Appearance(lit, unlit), passable=True, transparent=False)


# A passable, transparent tile marked as an exit
def exit_tile(lit, unlit):
    return TileType(Appearance(lit, unlit), passable=True, transparent=True, is_exit=True, always_visible=True)


TileType.FLOOR = open_tile(Glyph(None, COLOR_LIGHT_GROUND),
                           Glyph(None, COLOR_DARK_GROUND))
TileType.WALL = solid_tile(Glyph(None, COLOR_LIGHT_WALL),
                           Glyph(None, COLOR_DARK_WALL))
TileType.STAIRS = exit_tile(Glyph('>', libtcod.white, COLOR_LIGHT_GROUND),
                            Glyph('>', libtcod.white, COLOR_DARK_GROUND))
TileType.TALL_GRASS = fog_tile(Glyph(':', libtcod.green, COLOR_LIGHT_GRASS),
                               Glyph(':', COLOR_DARK_GROUND))
TileType.CRUSHED_GRASS = open_tile(Glyph('.', libtcod.green, COLOR_LIGHT_GROUND),
                                   Glyph('.', COLOR_DARK_GROUND))
TileType.OPEN_DOOR = open_tile(Glyph('-', libtcod.white, COLOR_LIGHT_GROUND),
                               Glyph('-', libtcod.white, COLOR_DARK_GROUND))
TileType.CLOSED_DOOR = solid_tile(Glyph('+', libtcod.white, COLOR_LIGHT_WALL),
                                  Glyph('+', libtcod.white, COLOR_DARK_WALL))
TileType.TALL_GRASS.steps_to = TileType.CRUSHED_GRASS
TileType.OPEN_DOOR.closes_to = TileType.CLOSED_DOOR
TileType.CLOSED_DOOR.opens_to = TileType.OPEN_DOOR


class Tile:
    def __init__(self):
        self.type = TileType.WALL
        self.explored = False

    @property
    def passable(self):
        return self.type.passable

    @property
    def transparent(self):
        return self.type.transparent


class TileMeta:
    def __init__(self):
        self.room_wall = False
        self.tunnelled = False


class Map:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.tiles = [[Tile()
                       for _ in range(height)]
                      for _ in range(width)]
        self.fov_map = None
        self.visibility_dirty = True

    def __refresh_fov(self, fov_map):
        for y in range(self.height):
            for x in range(self.width):
                libtcod.map_set_properties(fov_map, x, y,
                                           self.tiles[x][y].transparent,
                                           self.tiles[x][y].passable)

    def tile(self, position):
        return self.tiles[position.x][position.y]

    def make_fov_map(self):
        # Create the FOV map according to the generated map
        fov_map = libtcod.map_new(self.width, self.height)
        self.__refresh_fov(fov_map)
        return fov_map

    def is_xy_in_fov(self, x, y):
        return libtcod.map_is_in_fov(self.fov_map, x, y)

    def is_in_fov(self, pos):
        return libtcod.map_is_in_fov(self.fov_map, pos.x, pos.y)

    def dirty_visibility(self):
        self.visibility_dirty = True

    def refresh_visibility(self, pos):
        if self.visibility_dirty:
            self.__refresh_fov(self.fov_map)
            libtcod.map_compute_fov(self.fov_map, pos.x, pos.y,
                                    TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGORITHM)
            self.visibility_dirty = False

    def is_on_map(self, position):
        x_in_bounds = 0 <= position.x < self.width
        y_in_bounds = 0 <= position.y < self.height
        return x_in_bounds and y_in_bounds

    def movement_blocked(self, x, y):
        return not self.tiles[x][y].passable

    def vision_blocked(self, x, y):
        return not self.tiles[x][y].transparent

    def is_explored(self, x, y):
        return self.tiles[x][y].explored

    def mark_explored(self, x, y):
        self.tiles[x][y].explored = True


class LevelBuilder:
    def __init__(self, game_map, game_actors, game_items, dungeon_level):
        self.map = game_map
        self.meta_map = [[TileMeta()
                          for _ in range(game_map.height)]
                         for _ in range(game_map.width)]
        self.game_actors = game_actors
        self.game_items = game_items
        self.dungeon_level = dungeon_level

    def finalize(self, game):
        self.map.fov_map = self.map.make_fov_map()
        self.map.refresh_visibility(game.player.pos)
        game.stage = Stage(self.map, self.game_actors, self.game_items)

    def mark_tunnelled(self, x, y):
        self.meta_map[x][y].tunnelled = True

    def create_room(self, room):
        # Go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.map.tiles[x][y].type = TileType.FLOOR

        # Mark the exterior tiles as walls
        for x in range(room.x1, room.x2+1):
            self.meta_map[x][room.y1].room_wall = True
            self.meta_map[x][room.y2].room_wall = True
        for y in range(room.y1, room.y2+1):
            self.meta_map[room.x1][y].room_wall = True
            self.meta_map[room.x2][y].room_wall = True

    def create_tunnel_to(self, previous_room, current_room):
        previous = previous_room.center()
        current = current_room.center()
        if libtcod.random_get_int(0, 0, 1) == 1:
            # First move horizontally, then vertically
            self._create_h_tunnel(previous.x, current.x, previous.y)
            self._create_v_tunnel(previous.y, current.y, current.x)
        else:
            # First move vertically, then horizontally
            self._create_v_tunnel(previous.y, current.y, previous.x)
            self._create_h_tunnel(previous.x, current.x, current.y)

    def _create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map.tiles[x][y].type = TileType.FLOOR
            if self.meta_map[x][y].room_wall:
                self.mark_tunnelled(x, y)

    def _create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map.tiles[x][y].type = TileType.FLOOR
            if self.meta_map[x][y].room_wall:
                self.mark_tunnelled(x, y)

    def place_stairs(self, room):
        position = room.center()
        self.map.tiles[position.x][position.y].type = TileType.STAIRS

    def _place_grass_tile(self, position):
        self.map.tiles[position.x][position.y].type = TileType.TALL_GRASS

    def place_grass(self, room):
        if libtcod.random_get_int(0, 1, 2) == 1:
            point = room.random_point_inside()
            while is_blocked(self.map, self.game_actors, point):
                point = room.random_point_inside()

            self._place_grass_tile(point)

            num_grass = libtcod.random_get_int(0, 4, 8)
            for i in range(num_grass):
                point = random_point_surrounding(point)
                while not self.map.is_on_map(point):
                    point = random_point_surrounding(point)

                if not is_blocked(self.map, self.game_actors, point):
                    self._place_grass_tile(point)

    CREATURE_CHANCES = dict(
        critter=[[6, 1], [5, 3], [4, 5], [3, 7], [2, 9]],
        mob=[[2, 1], [3, 4], [5, 6]]
    )

    def place_creatures(self, creature_type, room):
        creatures = filter(lambda m: m['type'] == creature_type, FACTORY.monster_templates)
        if len(creatures) == 0:
            return

        # Random number of creatures
        max_creatures = from_dungeon_level(self.CREATURE_CHANCES[creature_type], self.dungeon_level)
        num_creatures = libtcod.random_get_int(0, 0, max_creatures)
        creature_chances = get_spawn_chances(creatures, self.dungeon_level)

        chance = libtcod.random_get_int(0, 1, 100)
        if chance <= 5:
            num_creatures = max_creatures * 3

        for i in range(num_creatures):
            # Random position for creature
            point = room.random_point_inside()

            if not is_blocked(self.map, self.game_actors, point):
                choice = random_choice(creature_chances)
                creature = FACTORY.new_monster(choice, point)
                self.game_actors.append(creature)

    def place_boss(self, room):
        position = room.center()
        bosses = filter(lambda m: m['type'] == 'boss', FACTORY.monster_templates)
        if len(bosses) == 0:
            return

        # Randomly select a boss and place it near the center of the room
        boss = bosses[libtcod.random_get_int(0, 0, len(bosses)-1)]
        boss = FACTORY.new_monster(boss['name'], random_point_surrounding(position))
        self.game_actors.append(boss)

    def place_items(self, room):
        # Random number of items
        max_items = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)
        num_items = libtcod.random_get_int(0, 0, max_items)
        item_chances = get_spawn_chances(FACTORY.item_templates, self.dungeon_level)

        for i in range(num_items):
            # Random position for item
            point = room.random_point_inside()

            if not is_blocked(self.map, self.game_actors, point):
                choice = random_choice(item_chances)
                item = FACTORY.new_item(choice, point)
                self.game_items.append(item)

    def place_doors(self):
        # Look for tunnelled walls as potential doors
        for x in range(self.map.width):
            for y in range(self.map.height):
                if self.meta_map[x][y].tunnelled:
                    # Don't place doors next to other doors
                    door_above = self.meta_map[x][y+1].tunnelled
                    door_below = self.meta_map[x][y-1].tunnelled
                    door_left = self.meta_map[x-1][y].tunnelled
                    door_right = self.meta_map[x+1][y].tunnelled
                    if door_above or door_below or door_left or door_right:
                        continue

                    # Make sure to place doors between two walls
                    wall_above = self.meta_map[x][y+1].room_wall
                    wall_below = self.meta_map[x][y-1].room_wall
                    wall_left = self.meta_map[x-1][y].room_wall
                    wall_right = self.meta_map[x+1][y].room_wall
                    if (wall_above and wall_below) or (wall_left and wall_right):
                        self.map.tiles[x][y].type = TileType.CLOSED_DOOR


def random_choice_index(chances):
    # Choose an option from the list, returning its index
    dice = libtcod.random_get_int(0, 1, sum(chances))

    running_sum = 0
    choice = 0
    for i in chances:
        running_sum += i
        if dice <= running_sum:
            return choice
        choice += 1


def random_choice(chances_dict):
    # Choose one option from dictionary of chances, returning its key
    choices = chances_dict.keys()
    chances = chances_dict.values()
    return choices[random_choice_index(chances)]


def from_dungeon_level(table, dungeon_level):
    # Returns a value that depends on the dungeon level. The table specifies
    # what value occurs after each level. Default is 0.
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0


def get_spawn_chances(templates, dungeon_level):
    chances = {}
    for t in templates:
        if 'spawn' in t:
            chance = t['spawn']
            if isinstance(chance, list):
                chances[t['name']] = from_dungeon_level(chance, dungeon_level)
            else:
                chances[t['name']] = chance
    return chances


def random_point_surrounding(position):
    p = Position(libtcod.random_get_int(0, position.x-1, position.x+1),
                 libtcod.random_get_int(0, position.y-1, position.y+1))
    while p.x == position.x and p.y == position.y:
        p = Position(libtcod.random_get_int(0, position.x-1, position.x+1),
                     libtcod.random_get_int(0, position.y-1, position.y+1))
    return p


def room_overlaps_existing(room, existing):
    for other in existing:
        if room.intersect(other):
            return True
    return False


def randomly_placed_rect(game_map):
    # Random width and height
    w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)

    # Random position without going out of the boundaries of the map
    x = libtcod.random_get_int(0, 0, game_map.width - w - 1)
    y = libtcod.random_get_int(0, 0, game_map.height - h - 1)

    return Rect(x, y, w, h)


def make_map(game):
    actors = [game.player]
    items = []
    game_map = Map(MAP_HEIGHT, MAP_WIDTH)
    builder = LevelBuilder(game_map, actors, items, game.dungeon_level)
    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        room = randomly_placed_rect(game_map)

        # Throw the new room away if it overlaps with an existing one
        if room_overlaps_existing(room, rooms):
            continue

        # Room is valid, continue
        builder.create_room(room)

        if num_rooms == 0:
            # This is the first room, where the player starts at
            game.player.pos.copy(room.center())
        else:
            # Connect it to the previous room with a tunnel
            builder.create_tunnel_to(rooms[num_rooms - 1], room)

        # Finish
        builder.place_grass(room)
        builder.place_creatures('mob', room)
        builder.place_items(room)
        builder.place_creatures('critter', room)
        rooms.append(room)
        num_rooms += 1

    # Place doors now that we have rooms and corridors
    builder.place_doors()

    # Place stairs in the last room, along with a boss
    final_room = rooms[num_rooms - 1]
    builder.place_stairs(final_room)
    builder.place_boss(final_room)

    # Finalize level generation
    builder.finalize(game)
