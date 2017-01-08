import libtcodpy as libtcod
from pyro.gameobject import GameObject
import pyro.components.door as libdoor
import pyro.components.grass as libgrass
import pyro.utilities as libutils
from pyro.settings import *


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
        centerx = (self.x1 + self.x2) / 2
        centery = (self.y1 + self.y2) / 2
        return (centerx, centery)

    def intersect(self, other):
        # Returns true if this rectangle intersects with the other one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def random_point_inside(self):
        return Point(libtcod.random_get_int(0, self.x1+1, self.x2-1),
                     libtcod.random_get_int(0, self.y1+1, self.y2-1))


class Tile:
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        self.explored = False


class TileMeta:
    def __init__(self):
        self.room_wall = False
        self.tunnelled = False


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


def create_room(map, room, metamap):
    # Go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

    # Mark the exterior tiles as walls
    for x in range(room.x1, room.x2+1):
        metamap[x][room.y1].room_wall = True
        metamap[x][room.y2].room_wall = True
    for y in range(room.y1, room.y2+1):
        metamap[room.x1][y].room_wall = True
        metamap[room.x2][y].room_wall = True


def create_h_tunnel(map, x1, x2, y, metamap):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
        if metamap[x][y].room_wall:
            metamap[x][y].tunnelled = True


def create_v_tunnel(map, y1, y2, x, metamap):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
        if metamap[x][y].room_wall:
            metamap[x][y].tunnelled = True


def get_spawn_chances(templates, dungeon_level):
    chances = {}
    for t in templates:
        if t.has_key('spawn'):
            chance = t['spawn']
            if isinstance(chance, list):
                chances[t['name']] = from_dungeon_level(chance, dungeon_level)
            else:
                chances[t['name']] = chance
    return chances


def place_door(x, y, map, objects):
    map[x][y].blocked = True
    map[x][y].block_sight = True
    door_comp = libdoor.Door(is_open=False, opened_glyph='-', closed_glyph='+')
    door = GameObject(x, y, '+', 'door', libtcod.white, render_order=0,
                      components={libdoor.Door: door_comp})
    objects.append(door)


def place_doors(map, objects, metamap):
    # Look for tunnelled walls as potential doors
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if metamap[x][y].tunnelled:
                # Don't place doors next to other doors
                door_above = metamap[x][y+1].tunnelled
                door_below = metamap[x][y-1].tunnelled
                door_left = metamap[x-1][y].tunnelled
                door_right = metamap[x+1][y].tunnelled
                if door_above or door_below or door_left or door_right:
                    continue

                # Make sure to place doors between two walls
                wall_above = map[x][y+1].blocked
                wall_below = map[x][y-1].blocked
                wall_left = map[x-1][y].blocked
                wall_right = map[x+1][y].blocked
                if (wall_above and wall_below) or (wall_left and wall_right):
                    place_door(x, y, map, objects)


def place_critters(room, map, objects, dungeon_level, object_factory):
    # Random number of critters
    max_critters = from_dungeon_level([[6, 1],
                                       [5, 3],
                                       [4, 5],
                                       [3, 7],
                                       [2, 9]],
                                      dungeon_level)
    num_critters = libtcod.random_get_int(0, 0, max_critters)
    critters = filter(lambda m: m['ai'] == 'passive_aggressive',
                      object_factory.monster_templates)
    critter_chances = get_spawn_chances(critters, dungeon_level)

    chance = libtcod.random_get_int(0, 1, 100)
    if chance <= 5:
        num_critters = max_critters * 3

    for i in range(num_critters):
        # Random position for critter
        point = room.random_point_inside()

        if not libutils.is_blocked(map, objects, point.x, point.y):
            choice = random_choice(critter_chances)
            critter = object_factory.new_monster(choice)
            critter.x = point.x
            critter.y = point.y
            objects.append(critter)


def place_monsters(room, map, objects, dungeon_level, object_factory):
    # Random number of monsters
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]], dungeon_level)
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)
    monsters = filter(lambda m: m['ai'] != 'passive_aggressive',
                      object_factory.monster_templates)
    monster_chances = get_spawn_chances(monsters, dungeon_level)

    chance = libtcod.random_get_int(0, 1, 100)
    if chance <= 5:
        num_monsters = max_monsters * 3

    for i in range(num_monsters):
        # Random position for monster
        point = room.random_point_inside()

        if not libutils.is_blocked(map, objects, point.x, point.y):
            choice = random_choice(monster_chances)
            monster = object_factory.new_monster(choice)
            monster.x = point.x
            monster.y = point.y
            objects.append(monster)


def place_items(room, map, objects, dungeon_level, object_factory):
    # Random number of items
    max_items = from_dungeon_level([[1, 1], [2, 4]], dungeon_level)
    num_items = libtcod.random_get_int(0, 0, max_items)
    item_chances = get_spawn_chances(object_factory.item_templates, dungeon_level)

    for i in range(num_items):
        # Random position for item
        point = room.random_point_inside()

        if not libutils.is_blocked(map, objects, point.x, point.y):
            choice = random_choice(item_chances)
            item = object_factory.new_item(choice)
            item.x = point.x
            item.y = point.y
            objects.append(item)


def place_grass_tile(x, y, map, objects):
    map[x][y].block_sight = True
    grass_comp = libgrass.Grass(is_crushed=False, standing_glyph=':',
                                crushed_glyph='.')
    grass = GameObject(x, y, ':', 'tall grass', libtcod.green,
                       render_order=0,
                       components={libgrass.Grass: grass_comp})
    objects.append(grass)


def random_point_surrounding(point):
    p = Point(libtcod.random_get_int(0, point.x-1, point.x+1),
              libtcod.random_get_int(0, point.y-1, point.y+1))
    while p.x == point.x and p.y == point.y:
        p = Point(libtcod.random_get_int(0, point.x-1, point.x+1),
                  libtcod.random_get_int(0, point.y-1, point.y+1))
    return p


def is_on_map(point, map):
    x_in_bounds = point.x >= 0 and point.x < len(map)
    y_in_bounds = point.y >= 0 and point.y < len(map[0])
    return x_in_bounds and y_in_bounds


def place_grass(room, map, objects):
    if libtcod.random_get_int(0, 1, 2) == 1:
        grass_tiles = []
        point = room.random_point_inside()
        while libutils.is_blocked(map, objects, point.x, point.y):
            point = room.random_point_inside()

        place_grass_tile(point.x, point.y, map, grass_tiles)

        num_grass = libtcod.random_get_int(0, 4, 8)
        for i in range(num_grass):
            point = random_point_surrounding(point)
            while not is_on_map(point, map):
                point = random_point_surrounding(point)

            grass_at_point = False
            for grass in grass_tiles:
                if point.x == grass.x and point.y == grass.y:
                    grass_at_point = True
                    break

            if grass_at_point:
                continue

            if not libutils.is_blocked(map, objects, point.x, point.y):
                place_grass_tile(point.x, point.y, map, objects)

        for grass in grass_tiles:
            objects.append(grass)


def room_overlaps_existing(room, existing):
    for other in existing:
        if room.intersect(other):
            return True
    return False


def randomly_placed_rect():
    # Random width and height
    w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)

    # Random position without going out of the boundaries of the map
    x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
    y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

    return Rect(x, y, w, h)


def make_map(player, dungeon_level, object_factory):
    objects = [player]
    map = [[Tile(True)
            for y in range(MAP_HEIGHT)]
           for x in range(MAP_WIDTH)]
    metamap = [[TileMeta()
                for y in range(MAP_HEIGHT)]
               for x in range(MAP_WIDTH)]
    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        new_room = randomly_placed_rect()

        # Throw the new room away if it overlaps with an existing one
        if room_overlaps_existing(new_room, rooms):
            continue

        # Room is valid, continue
        create_room(map, new_room, metamap)

        (new_x, new_y) = new_room.center()

        if num_rooms == 0:
            # This is the first room, where the player starts at
            player.x = new_x
            player.y = new_y
        else:
            # Connect it to the previous room with a tunnel

            # Center of the previous room
            (prev_x, prev_y) = rooms[num_rooms-1].center()

            if libtcod.random_get_int(0, 0, 1) == 1:
                # First move horizontally, then vertically
                create_h_tunnel(map, prev_x, new_x, prev_y, metamap)
                create_v_tunnel(map, prev_y, new_y, new_x, metamap)
            else:
                # First move vertically, then horizontally
                create_v_tunnel(map, prev_y, new_y, prev_x, metamap)
                create_h_tunnel(map, prev_x, new_x, new_y, metamap)

        # Finish
        place_grass(new_room, map, objects)
        place_monsters(new_room, map, objects, dungeon_level, object_factory)
        place_items(new_room, map, objects, dungeon_level, object_factory)
        place_critters(new_room, map, objects, dungeon_level, object_factory)
        rooms.append(new_room)
        num_rooms += 1

    place_doors(map, objects, metamap)

    # Create stairs at the center of the last room
    stairs = GameObject(new_x, new_y, '>', 'stairs', libtcod.white,
                        render_order=0, always_visible=True)
    objects.append(stairs)

    return (map, objects, stairs)
