

def is_blocked(game_map, objects, x, y):
    # First test the map tile
    if game_map.movement_blocked(x, y):
        return True

    # Now check for any blocking objects
    for game_object in objects:
        if game_object.blocks and game_object.x == x and game_object.y == y:
            return True

    return False
