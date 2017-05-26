import tcod as libtcod
from itertools import chain
import pyro.objects as objects
from pyro.engine.game import Game
from pyro.map import make_map
from pyro.settings import SCREEN_HEIGHT, SCREEN_WIDTH, LIMIT_FPS
from pyro.settings import MSG_X, BAR_WIDTH, PANEL_HEIGHT, PANEL_Y, MAP_WIDTH, MAP_HEIGHT
from pyro.ui.game_screen import GameScreen
from pyro.ui.userinterface import UserInterface
from pyro.ui.keys import key_for_int, Key
from pyro.ui.inputs import Input


###############################################################################
# User Interface                                                              #
###############################################################################


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
    if 0 <= index < len(options):
        return index
    else:
        return None


def get_names_under_mouse(mouse, game):
    # Return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    # Create a list with the names of all objects at the mouse's coordinates
    # and in FOV
    names = [obj.name for obj in chain(game.stage.actors, game.stage.items, game.stage.corpses)
             if obj.pos.equals(x, y) and game.stage.map.is_in_fov(obj.pos)]
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
    libtcod.console_clear(ui.console)
    libtcod.console_clear(ui.panel)

    # Draw tiles
    for y in range(game.stage.map.height):
        for x in range(game.stage.map.width):
            tile = game.stage.map.tiles[x][y]
            visible = game.stage.map.is_xy_in_fov(x, y)
            if not visible:
                if tile.explored:
                    glyph = tile.type.appearance.unlit
                    libtcod.console_set_char_background(ui.console, x, y, glyph.bg_color, libtcod.BKGND_SET)
                    if tile.type.always_visible and glyph.char:
                        libtcod.console_set_default_foreground(ui.console, glyph.fg_color)
                        libtcod.console_put_char(ui.console, x, y, glyph.char, libtcod.BKGND_NONE)
            else:
                tile.explored = True
                glyph = tile.type.appearance.lit
                libtcod.console_set_char_background(ui.console, x, y, glyph.bg_color, libtcod.BKGND_SET)
                if glyph.char:
                    libtcod.console_set_default_foreground(ui.console, glyph.fg_color)
                    libtcod.console_put_char(ui.console, x, y, glyph.char, libtcod.BKGND_NONE)

    # Draw game items
    for item in game.stage.items:
        if game.stage.map.is_in_fov(item.pos):
            libtcod.console_set_default_foreground(ui.console, item.glyph.fg_color)
            libtcod.console_put_char(ui.console, item.pos.x, item.pos.y,
                                     item.glyph.char, libtcod.BKGND_NONE)

    # Draw corpses
    for corpse in game.stage.corpses:
        if game.stage.map.is_in_fov(corpse.pos):
            glyph = corpse.type.glyph
            libtcod.console_set_default_foreground(ui.console, glyph.fg_color)
            libtcod.console_put_char(ui.console, corpse.pos.x, corpse.pos.y,
                                     glyph.char, libtcod.BKGND_NONE)

    # Draw game actors
    for actor in game.stage.actors:
        if game.stage.map.is_in_fov(actor.pos):
            libtcod.console_set_default_foreground(ui.console, actor.glyph.fg_color)
            libtcod.console_put_char(ui.console, actor.pos.x, actor.pos.y,
                                     actor.glyph.char, libtcod.BKGND_NONE)

    # Blit the contents of the game (non-GUI) console to the root console
    libtcod.console_blit(ui.console, 0, 0, game.stage.map.width, game.stage.map.height, 0, 0, 0)

    # Print game messages, one line at a time
    y = 1
    for (line, color) in game.log.messages:
        libtcod.console_set_default_foreground(ui.panel, color)
        libtcod.console_print_ex(ui.panel, MSG_X, y, libtcod.BKGND_NONE,
                                 libtcod.LEFT, line)
        y += 1

    # Show player's stats
    render_ui_bar(ui.panel, 1, 1, BAR_WIDTH, 'HP', game.player.hp,
                  game.player.max_hp, libtcod.light_red, libtcod.darker_red)
    render_ui_bar(ui.panel, 1, 2, BAR_WIDTH, 'EXP', game.player.xp,
                  game.player.required_for_level_up(), libtcod.green, libtcod.darkest_green)

    # Show the dungeon level
    libtcod.console_print_ex(ui.panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Dungeon Level {}'.format(game.dungeon_level))

    # Display names of objects under the mouse
    names = get_names_under_mouse(ui.mouse, game)
    libtcod.console_set_default_foreground(ui.panel, libtcod.light_gray)
    libtcod.console_print_ex(ui.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             names)

    # Reset the background color for next time
    libtcod.console_set_default_background(ui.panel, libtcod.black)

    # Blit the contents of the GUI panel to the root console
    libtcod.console_blit(ui.panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

    libtcod.console_flush()


###############################################################################
# Game Logic                                                                  #
###############################################################################


def new_game():
    game = Game(state='playing', dungeon_level=1)
    player = objects.new_player(game)
    game.player = player
    make_map(game)

    game.log.messages = []
    m = 'Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings!'
    game.log.message(m, libtcod.red)

    return game


def play_game(game, ui):
    # TODO Delete this once MainMenuScreen -> GameScreen
    ui.screens = []
    ui.push(GameScreen(game))
    while not libtcod.console_is_window_closed():
        ui.refresh()

        key = check_for_input(ui)
        if key:
            ui.handle_input(key)

        if game.state == 'exit':
            break


def check_for_input(ui):
    result = None
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS |
                                libtcod.EVENT_MOUSE, ui.keyboard, ui.mouse)
    k = libtcod.console_check_for_keypress()
    if k.vk != libtcod.KEY_NONE:
        result = key_for_int(ui.keyboard.c)
    elif libtcod.KEY_LEFT == ui.keyboard.vk:
        result = Key.LEFT
    elif libtcod.KEY_RIGHT == ui.keyboard.vk:
        result = Key.RIGHT
    elif libtcod.KEY_UP == ui.keyboard.vk:
        result = Key.UP
    elif libtcod.KEY_DOWN == ui.keyboard.vk:
        result = Key.DOWN
    elif libtcod.KEY_ENTER == ui.keyboard.vk:
        result = Key.ENTER
    elif libtcod.KEY_ESCAPE == ui.keyboard.vk:
        result = Key.ESCAPE
    return result


def main_menu(ui):
    background = libtcod.image_load('resources/menu_background.png')

    while not libtcod.console_is_window_closed():
        # Show the image at twice the regular console resolution
        libtcod.image_blit_2x(background, 0, 0, 0)

        # Show options and wait for the player's choice
        options = ['Play a new game', 'Quit']
        choice = menu(ui.console, '', options, 24)

        if choice == 0:
            # New game
            game = new_game()
            play_game(game, ui)
        elif choice == 1:
            # Quit
            break


###############################################################################
# Initialization & Main Loop                                                  #
###############################################################################


class OldUserInterface:
    def __init__(self):
        self.keyboard = libtcod.Key()
        self.mouse = libtcod.Mouse()
        self.console = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
        self.panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

    def render_all(self, game, fov_recompute):
        render_all(self, game, fov_recompute)


libtcod.console_set_custom_font('resources/terminal8x12_gs_tc.png',
                                libtcod.FONT_TYPE_GREYSCALE |
                                libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
                          'Tombs Of The Ancient Kings', False)
libtcod.sys_set_fps(LIMIT_FPS)

ui = UserInterface(OldUserInterface())

ui.bind_key(Key.ESCAPE, Input.EXIT)
ui.bind_key(Key.ENTER, Input.ENTER)
ui.bind_key(Key.UP, Input.NORTH)
ui.bind_key(Key.DOWN, Input.SOUTH)
ui.bind_key(Key.LEFT, Input.WEST)
ui.bind_key(Key.RIGHT, Input.EAST)
ui.bind_key(Key.C, Input.HERO_INFO)
ui.bind_key(Key.G, Input.PICKUP)
ui.bind_key(Key.D, Input.DROP)
ui.bind_key(Key.I, Input.INVENTORY)
ui.bind_key(Key.F, Input.REST)
ui.bind_key(Key.R, Input.CLOSE_DOOR)

main_menu(ui)
