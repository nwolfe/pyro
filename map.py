import libtcodpy as libtcod
import object as libobj
from settings import *


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


class Tile:
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        self.explored = False


def create_room(map, room):
    # Go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False


def create_h_tunnel(map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def create_v_tunnel(map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def place_objects(room, map, objects):
    # Random number of numbers
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    for i in range(num_monsters):
        # Random position for monster
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not libobj.is_blocked(map, objects, x, y):
            dice = libtcod.random_get_int(0, 0, 100)
            if dice < 80:
                # Create orc (80% chance)
                monster = libobj.make_orc(x, y)
            else:
                # Create troll (20% chance)
                monster = libobj.make_troll(x, y)
            objects.append(monster)

    # Random number of items
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

    for i in range(num_items):
        # Random position for item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        if not libobj.is_blocked(map, objects, x, y):
            dice = libtcod.random_get_int(0, 0, 100)
            if dice < 70:
                # Create healing potion (70% chance)
                item = libobj.make_healing_potion(x, y)
            elif dice < 85:
                # Create a lightning bolt scroll (15% chance)
                item = libobj.make_lightning_scroll(x, y)
            else:
                # Create a confusion scroll (15% chance)
                item = libobj.make_confusion_scroll(x, y)
            objects.append(item)


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


def make_map(player, objects):
    map = [[Tile(True)
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
        create_room(map, new_room)

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
                create_h_tunnel(map, prev_x, new_x, prev_y)
                create_v_tunnel(map, prev_y, new_y, new_x)
            else:
                # First move vertically, then horizontally
                create_v_tunnel(map, prev_y, new_y, prev_x)
                create_h_tunnel(map, prev_x, new_x, new_y)

        # Finish
        place_objects(new_room, map, objects)
        rooms.append(new_room)
        num_rooms += 1

    return map
