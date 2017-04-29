import tcod as libtcod


def blocked(game, position):
    return is_blocked(game.map, game.actors, position.x, position.y)


def is_blocked(game_map, actors, x, y):
    # First test the map tile
    if game_map.movement_blocked(x, y):
        return True

    # Now check for any blocking objects
    for actor in actors:
        if actor.pos.equal_to(x, y):
            return True

    return False


def target_tile(game, ui, max_range=None):
    # Return the position of a tile left-clicked in player's FOV
    # (optionally in a range), or (None, None) if right-clicked.
    while True:
        # Render the screen. This erases the inventory and shows the names of
        # objects under the mouse.
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE,
                                    ui.keyboard, ui.mouse)
        ui.render_all(game, False)

        (x, y) = (ui.mouse.cx, ui.mouse.cy)

        if (ui.mouse.lbutton_pressed and game.map.is_xy_in_fov(x, y) and
                (max_range is None or game.player.pos.distance(x, y) <= max_range)):
            return x, y

        if ui.mouse.rbutton_pressed or ui.keyboard.vk == libtcod.KEY_ESCAPE:
            return None, None


def target_monster(game, ui, max_range=None):
    # Returns a clicked monster inside FOV up to a range, or None if
    # right-clicked
    while True:
        (x, y) = target_tile(game, ui, max_range)
        if x is None:
            return None

        # Return the first clicked monster, otherwise continue looking
        for game_object in game.actors:
            if game_object != game.player:
                if game_object.pos.equal_to(x, y):
                    return game_object


def closest_monster(game, max_range):
    # Find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1

    for game_object in game.actors:
        if game_object != game.player:
            if game.map.is_in_fov(game_object.pos):
                # Calculate distance between this object and the player
                dist = game.player.pos.distance_to(game_object.pos)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_enemy = game_object

    return closest_enemy
