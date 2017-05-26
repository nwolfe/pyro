import tcod as libtcod
from itertools import chain
from pyro.settings import SCREEN_HEIGHT, SCREEN_WIDTH, LIMIT_FPS
from pyro.settings import MSG_X, BAR_WIDTH, PANEL_HEIGHT, PANEL_Y, MAP_WIDTH, MAP_HEIGHT
from pyro.ui.main_menu_screen import MainMenuScreen
from pyro.ui.userinterface import UserInterface
from pyro.ui.keys import Key
from pyro.ui.inputs import Input


###############################################################################
# User Interface                                                              #
###############################################################################

class OldUserInterface:
    def __init__(self):
        self.keyboard = libtcod.Key()
        self.mouse = libtcod.Mouse()
        self.console = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
        self.panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

    def render_all(self, game, fov_recompute):
        render_all(self, game, fov_recompute)


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
# Initialization & Main Loop                                                  #
###############################################################################

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

ui.push(MainMenuScreen())

while ui.is_running():
    ui.refresh()
    ui.handle_input()
