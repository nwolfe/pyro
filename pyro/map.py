import tcod as libtcod
from pyro.utilities import is_blocked
from pyro.settings import ROOM_MIN_SIZE, ROOM_MAX_SIZE, MAP_HEIGHT, MAP_WIDTH, MAX_ROOMS
from pyro.settings import COLOR_LIGHT_GROUND, COLOR_DARK_GROUND, COLOR_LIGHT_WALL, COLOR_DARK_WALL, COLOR_LIGHT_GRASS
from pyro.settings import TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGORITHM


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return center_x, center_y

    def intersect(self, other):
        # Returns true if this rectangle intersects with the other one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def random_point_inside(self):
        return Point(libtcod.random_get_int(0, self.x1+1, self.x2-1),
                     libtcod.random_get_int(0, self.y1+1, self.y2-1))


class Glyph:
    def __init__(self, char, fg_color, bg_color=None):
        self.char = char
        self.fg_color = fg_color
        self.bg_color = bg_color if bg_color else fg_color


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
        self.visibility_dirty = False

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

    def is_in_fov(self, x, y):
        return libtcod.map_is_in_fov(self.fov_map, x, y)

    def dirty_visibility(self):
        self.visibility_dirty = True

    def refresh_visibility(self, pos):
        if self.visibility_dirty:
            self.__refresh_fov(self.fov_map)
            libtcod.map_compute_fov(self.fov_map, pos.x, pos.y,
                                    TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGORITHM)
            self.visibility_dirty = False

    def is_on_map(self, x, y):
        x_in_bounds = 0 <= x < self.width
        y_in_bounds = 0 <= y < self.height
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
    def __init__(self, game_map, game_objects, game_items, game_object_factory, dungeon_level):
        self.map = game_map
        self.meta_map = [[TileMeta()
                          for _ in range(game_map.height)]
                         for _ in range(game_map.width)]
        self.game_objects = game_objects
        self.game_items = game_items
        self.game_object_factory = game_object_factory
        self.dungeon_level = dungeon_level

    def finalize(self, game):
        self.map.fov_map = self.map.make_fov_map()
        self.map.dirty_visibility()
        self.map.refresh_visibility(game.player.pos)
        game.map = self.map
        game.objects = self.game_objects
        game.items = self.game_items

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

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map.tiles[x][y].type = TileType.FLOOR
            if self.meta_map[x][y].room_wall:
                self.mark_tunnelled(x, y)

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map.tiles[x][y].type = TileType.FLOOR
            if self.meta_map[x][y].room_wall:
                self.mark_tunnelled(x, y)

    def place_stairs(self, x, y):
        self.map.tiles[x][y].type = TileType.STAIRS

    def place_grass_tile(self, x, y):
        self.map.tiles[x][y].type = TileType.TALL_GRASS

    def place_grass(self, room):
        if libtcod.random_get_int(0, 1, 2) == 1:
            point = room.random_point_inside()
            while is_blocked(self.map, self.game_objects, point.x, point.y):
                point = room.random_point_inside()

            self.place_grass_tile(point.x, point.y)

            num_grass = libtcod.random_get_int(0, 4, 8)
            for i in range(num_grass):
                point = random_point_surrounding(point)
                while not self.map.is_on_map(point.x, point.y):
                    point = random_point_surrounding(point)

                if not is_blocked(self.map, self.game_objects, point.x, point.y):
                    self.place_grass_tile(point.x, point.y)

    CREATURE_CHANCES = dict(
        critter=[[6, 1], [5, 3], [4, 5], [3, 7], [2, 9]],
        mob=[[2, 1], [3, 4], [5, 6]]
    )

    def place_creatures(self, creature_type, room):
        creatures = filter(lambda m: m['type'] == creature_type, self.game_object_factory.monster_templates)
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

            if not is_blocked(self.map, self.game_objects, point.x, point.y):
                choice = random_choice(creature_chances)
                creature = self.game_object_factory.new_monster(choice)
                creature.pos.x = point.x
                creature.pos.y = point.y
                self.game_objects.append(creature)

    def place_boss(self, room_x, room_y):
        bosses = filter(lambda m: m['type'] == 'boss', self.game_object_factory.monster_templates)
        if len(bosses) == 0:
            return

        # Randomly select a boss and place it near the center of the room
        boss = bosses[libtcod.random_get_int(0, 0, len(bosses)-1)]
        boss = self.game_object_factory.new_monster(boss['name'])
        nearby = random_point_surrounding(Point(room_x, room_y))
        boss.pos.x, boss.pos.y = nearby.x, nearby.y
        self.game_objects.append(boss)

    def place_items(self, room):
        # Random number of items
        max_items = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)
        num_items = libtcod.random_get_int(0, 0, max_items)
        item_chances = get_spawn_chances(self.game_object_factory.item_templates, self.dungeon_level)

        for i in range(num_items):
            # Random position for item
            point = room.random_point_inside()

            if not is_blocked(self.map, self.game_objects, point.x, point.y):
                choice = random_choice(item_chances)
                item = self.game_object_factory.new_item(choice)
                item.pos.x = point.x
                item.pos.y = point.y
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


def random_point_surrounding(point):
    p = Point(libtcod.random_get_int(0, point.x-1, point.x+1),
              libtcod.random_get_int(0, point.y-1, point.y+1))
    while p.x == point.x and p.y == point.y:
        p = Point(libtcod.random_get_int(0, point.x-1, point.x+1),
                  libtcod.random_get_int(0, point.y-1, point.y+1))
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


def make_map(game, object_factory):
    objects = [game.player]
    items = []
    game_map = Map(MAP_HEIGHT, MAP_WIDTH)
    builder = LevelBuilder(game_map, objects, items, object_factory, game.dungeon_level)
    rooms = []
    num_rooms = 0
    new_x = 0
    new_y = 0

    for r in range(MAX_ROOMS):
        new_room = randomly_placed_rect(game_map)

        # Throw the new room away if it overlaps with an existing one
        if room_overlaps_existing(new_room, rooms):
            continue

        # Room is valid, continue
        builder.create_room(new_room)

        (new_x, new_y) = new_room.center()

        if num_rooms == 0:
            # This is the first room, where the player starts at
            game.player.pos.x = new_x
            game.player.pos.y = new_y
        else:
            # Connect it to the previous room with a tunnel

            # Center of the previous room
            (prev_x, prev_y) = rooms[num_rooms-1].center()

            if libtcod.random_get_int(0, 0, 1) == 1:
                # First move horizontally, then vertically
                builder.create_h_tunnel(prev_x, new_x, prev_y)
                builder.create_v_tunnel(prev_y, new_y, new_x)
            else:
                # First move vertically, then horizontally
                builder.create_v_tunnel(prev_y, new_y, prev_x)
                builder.create_h_tunnel(prev_x, new_x, new_y)

        # Finish
        builder.place_grass(new_room)
        builder.place_creatures('mob', new_room)
        builder.place_items(new_room)
        builder.place_creatures('critter', new_room)
        rooms.append(new_room)
        num_rooms += 1

    builder.place_doors()

    # Create stairs at the center of the last room
    builder.place_stairs(new_x, new_y)

    # Put a boss near the stairs
    builder.place_boss(new_x, new_y)

    builder.finalize(game)
