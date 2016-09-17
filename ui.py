import libtcodpy as libtcod
from settings import *


class UserInterface:
    def __init__(self, console, panel):
        self.console = console
        self.panel = panel


def menu(console, header, options, width):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')

    # Calculate total height for header (after auto-wrap),
    # and one line per option
    if header == '':
        header_height = 0
    else:
        header_height = libtcod.console_get_height_rect(console, 0, 0, width,
                                                        SCREEN_HEIGHT, header)
    height = len(options) + header_height

    # Create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    # Print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height,
                                  libtcod.BKGND_NONE, libtcod.LEFT, header)

    # Print all the options
    y = header_height
    letter_index = ord('a')
    for option in options:
        text = '({0}) {1}'.format(chr(letter_index), option)
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE,
                                 libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # Blit the contents of the menu window to the root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # Present the root console to the player and wait for a key press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt-Enter toggles fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    # Convert ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options):
        return index
    else:
        return None


def messagebox(console, text, width=50):
    return menu(console, text, [], width)


def inventory_menu(console, inventory, header):
    # Show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty']
    else:
        options = []
        for item in inventory:
            text = item.name
            if item.equipment and item.equipment.is_equipped:
                text = '{0} (on {1})'.format(text, item.equipment.slot)
            options.append(text)
    selection_index = menu(console, header, options, INVENTORY_WIDTH)
    if selection_index is None or len(inventory) == 0:
        return None
    else:
        return inventory[selection_index].item


def get_names_under_mouse(mouse, objects, fov_map):
    # Return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    # Create a list with the names of all objects at the mouse's coordinates
    # and in FOV
    names = [obj.name for obj in objects
             if obj.x == x and obj.y == y and
             libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
    return ', '.join(names).capitalize()


def render_ui_bar(panel, x, y, total_width, name, value, maximum, bar_color,
                  back_color):
    # Render a bar (HP, experience, etc)
    bar_width = int(float(value) / maximum * total_width)

    # Render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False,
                         libtcod.BKGND_SCREEN)

    # Now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False,
                             libtcod.BKGND_SCREEN)

    # Finally, some centering text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y,
                             libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))


def render_all(ui, game, fov_recompute):
    if fov_recompute:
        # Recompute FOV if needed (i.e. the player moved)
        libtcod.map_compute_fov(game.fov_map, game.player.x, game.player.y,
                                TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        # Set tile background colors according to FOV
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(game.fov_map, x, y)
                wall = game.map[x][y].block_sight
                if not visible:
                    if game.map[x][y].explored:
                        color = COLOR_DARK_WALL if wall else COLOR_DARK_GROUND
                        libtcod.console_set_char_background(ui.console,
                                                            x, y, color,
                                                            libtcod.BKGND_SET)
                else:
                    color = COLOR_LIGHT_WALL if wall else COLOR_LIGHT_GROUND
                    libtcod.console_set_char_background(ui.console,
                                                        x, y, color,
                                                        libtcod.BKGND_SET)
                    game.map[x][y].explored = True

    render_ordered = sorted(game.objects, key=lambda obj: obj.render_order)
    for object in render_ordered:
        if libtcod.map_is_in_fov(game.fov_map, object.x, object.y):
            object.draw(ui.console)

    # Blit the contents of the game (non-GUI) console to the root console
    libtcod.console_blit(ui.console, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

    # Prepare to render the GUI panel
    libtcod.console_set_default_background(ui.panel, libtcod.black)
    libtcod.console_clear(ui.panel)

    # Print game messages, one line at a time
    y = 1
    for (line, color) in game.messages:
        libtcod.console_set_default_foreground(ui.panel, color)
        libtcod.console_print_ex(ui.panel, MSG_X, y, libtcod.BKGND_NONE,
                                 libtcod.LEFT, line)
        y += 1

    # Show player's stats
    render_ui_bar(ui.panel, 1, 1, BAR_WIDTH, 'HP', game.player.fighter.hp,
                  game.player.fighter.max_hp(game), libtcod.light_red,
                  libtcod.darker_red)

    # Show the dungeon level
    libtcod.console_print_ex(ui.panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Dungeon Level {}'.format(game.dungeon_level))

    # Display names of objects under the mouse
    names = get_names_under_mouse(game.mouse, game.objects, game.fov_map)
    libtcod.console_set_default_foreground(ui.panel, libtcod.light_gray)
    libtcod.console_print_ex(ui.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             names)

    # Blit the contents of the GUI panel to the root console
    libtcod.console_blit(ui.panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0,
                         PANEL_Y)
