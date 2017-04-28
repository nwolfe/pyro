import math
import tcod as libtcod
import pyro.direction


def astar(game, from_pos, to_pos):
    # Create a FOV map that has the dimensions of the map
    fov = game.map.make_fov_map()

    # Scan all the objects to see if there are objects that must be
    # navigated around. Check also that the object isn't self or the
    # target (so that the start and the end points are free).
    # The AI class handles the situation if self is next to the target so
    # it will not use this A* function anyway.
    for actor in game.actors:
        if actor.pos.x != to_pos.x and actor.pos.y != to_pos.y:
            # Set the tile as a wall so it must be navigated around
            libtcod.map_set_properties(fov, actor.pos.x, actor.pos.y, isTrans=True, isWalk=False)

    # Allocate an A* path
    # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0
    # if diagonal moves are prohibited
    path = libtcod.path_new_using_map(fov, 1.41)

    # Compute the path between self's coordinates and the target's coordinates
    libtcod.path_compute(path, from_pos.x, from_pos.y, to_pos.x, to_pos.y)

    # Check if the path exists, and in this case, also the path is shorter
    # than 25 tiles. The path size matters if you want the monster to use
    # alternative longer paths (for example through other rooms). It makes
    # sense to keep path size relatively low to keep the monsters from
    # running around the map if there's an alternative path really far away
    if not libtcod.path_is_empty(path) and libtcod.path_size(path) < 25:
        # Find the next coordinates in the computed full path
        next_x, next_y = libtcod.path_walk(path, True)
        libtcod.path_delete(path)
        return pyro.direction.from_vector(next_x - from_pos.x, next_y - from_pos.y)
    else:
        # Keep the old move function as a backup so that if there are no
        # paths (for example, another monster blocks a corridor). It will
        # still try to move towards the player (closer to the corridor opening).
        # Vector from this object to the target, and distance
        dx = to_pos.x - from_pos.x
        dy = to_pos.y - from_pos.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        libtcod.path_delete(path)
        return pyro.direction.from_vector(dx, dy)
