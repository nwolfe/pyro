from pyro.components import Physics


def is_blocked(game_map, objects, x, y):
    # First test the map tile
    if game_map.movement_blocked(x, y):
        return True

    # Now check for any blocking objects
    for game_object in objects:
        blocks = game_object.component(Physics).blocks
        if blocks and game_object.pos.equal_to(x, y):
            return True

    return False
