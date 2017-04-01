import math
import tcod as libtcod
from pyro.component import Component


class Movement(Component):
    def __init__(self):
        Component.__init__(self, component_type=Movement)

    def move(self, dx, dy):
        if not self.owner.game.is_blocked(self.owner.pos.x + dx, self.owner.pos.y + dy):
            self.owner.pos.x += dx
            self.owner.pos.y += dy
            return True
        else:
            return False

    def move_towards(self, target_x, target_y):
        # Vector from this object to the target, and distance
        dx = target_x - self.owner.pos.x
        dy = target_y - self.owner.pos.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def move_astar(self, target_x, target_y, passthrough=False):
        # Create a FOV map that has the dimensions of the map
        fov = self.owner.game.map.make_fov_map()

        # Scan all the objects to see if there are objects that must be
        # navigated around. Check also that the object isn't self or the
        # target (so that the start and the end points are free).
        # The AI class handles the situation if self is next to the target so
        # it will not use this A* function anyway.
        # Things like projectiles should just "pass through" objects rather
        # than fly around them.
        if not passthrough:
            for obj in self.owner.game.objects:
                if obj.blocks and obj != self.owner and obj.pos.x != target_x and obj.pos.y != target_y:
                    # Set the tile as a wall so it must be navigated around
                    libtcod.map_set_properties(fov, obj.pos.x, obj.pos.y, isTrans=True, isWalk=False)

        # Allocate an A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0
        # if diagonal moves are prohibited
        path = libtcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(path, self.owner.pos.x, self.owner.pos.y, target_x, target_y)

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
                self.owner.pos.x = next_x
                self.owner.pos.y = next_y
        else:
            # Keep the old move function as a backup so that if there are no
            # paths (for example, another monster blocks a corridor). It will
            # still try to move towards the player (closer to the corridor opening)
            self.move_towards(target_x, target_y)

        # Delete the path to free memory
        libtcod.path_delete(path)
