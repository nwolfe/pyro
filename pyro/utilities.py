

def blocked(game, position):
    return is_blocked(game.stage.map, game.stage.actors, position)


def is_blocked(game_map, actors, position):
    # First test the map tile
    if game_map.movement_blocked(position.x, position.y):
        return True

    # Now check for any blocking objects
    for actor in actors:
        if actor.pos == position:
            return True

    return False


def closest_monster(game, max_range):
    # Find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1

    for game_object in game.stage.actors:
        if game_object != game.player:
            if game.stage.map.is_in_fov(game_object.pos):
                # Calculate distance between this object and the player
                dist = game.player.pos.distance_to(game_object.pos)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_enemy = game_object

    return closest_enemy
