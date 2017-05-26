from itertools import chain
import tcod as libtcod
from pyro.settings import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT
from pyro.settings import PANEL_HEIGHT, MSG_X, BAR_WIDTH, PANEL_Y
from pyro.ui.keys import key_for_int, Key


class UserInterface:
    def __init__(self):
        self.screens = []
        self._keybindings = {}
        self.keyboard = libtcod.Key()
        self.mouse = libtcod.Mouse()
        self.console = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
        self.panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

    def render_all(self, game):
        _render_all(self, game)

    def bind_key(self, key, input_):
        self._keybindings[key] = input_

    def push(self, screen, tag=None):
        screen.tag = tag
        screen.bind(self)
        self.screens.append(screen)
        self.render()

    def pop(self, result=None):
        screen = self.screens.pop()
        screen.unbind()
        if len(self.screens) > 0:
            self.top_screen().activate(result, screen.tag)
            self.render()

    def refresh(self):
        for screen in self.screens:
            screen.update()
        # TODO Only render if dirty?
        self.render()

    def render(self):
        libtcod.console_clear(self.console)
        libtcod.console_clear(self.panel)

        index = len(self.screens) - 1
        while index >= 0:
            if not self.screens[index].transparent:
                break
            index -= 1

        if index < 0:
            index = 0

        while index < len(self.screens):
            self.screens[index].render()
            index += 1

        # TODO reset dirty flag here
        libtcod.console_flush()

    def handle_input(self):
        key = self._check_for_keypress()
        if key:
            screen = self.top_screen()
            if key in self._keybindings:
                if screen.handle_input(self._keybindings[key]):
                    return
            screen.handle_key_press(key)

    def top_screen(self):
        return self.screens[len(self.screens) - 1]

    def is_running(self):
        return not libtcod.console_is_window_closed() and len(self.screens) > 0

    def _check_for_keypress(self):
        result = None
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS |
                                    libtcod.EVENT_MOUSE, self.keyboard, self.mouse)
        k = libtcod.console_check_for_keypress()
        if k.vk != libtcod.KEY_NONE:
            result = key_for_int(self.keyboard.c)
        elif libtcod.KEY_LEFT == self.keyboard.vk:
            result = Key.LEFT
        elif libtcod.KEY_RIGHT == self.keyboard.vk:
            result = Key.RIGHT
        elif libtcod.KEY_UP == self.keyboard.vk:
            result = Key.UP
        elif libtcod.KEY_DOWN == self.keyboard.vk:
            result = Key.DOWN
        elif libtcod.KEY_ENTER == self.keyboard.vk:
            result = Key.ENTER
        elif libtcod.KEY_ESCAPE == self.keyboard.vk:
            result = Key.ESCAPE
        return result


class Screen:
    def __init__(self):
        self.ui = None
        self.transparent = False
        self.tag = None

    def bind(self, ui):
        self.ui = ui

    def unbind(self):
        self.ui = None

    def activate(self, result=None, tag=None):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def handle_input(self, input_):
        return False

    def handle_key_press(self, key):
        pass


# TODO This seems inappropriate in this userinterface module.
# Where should this function live?
def draw_menu(console, header, options, width, empty_text=None):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')

    if len(options) == 0 and empty_text:
        options = [empty_text]

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
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # Blit the contents of the menu window to the root console
    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)


# TODO Delete in favor of a Screen
def _get_names_under_mouse(mouse, game):
    # Return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    # Create a list with the names of all objects at the mouse's coordinates
    # and in FOV
    names = [obj.name for obj in chain(game.stage.actors, game.stage.items, game.stage.corpses)
             if obj.pos.equals(x, y) and game.stage.map.is_in_fov(obj.pos)]
    return ', '.join(names).capitalize()


# TODO Delete in favor of a Screen
def _render_ui_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    # Render a bar (HP, experience, etc)
    bar_width = int(float(value) / maximum * total_width)

    # Render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    # Now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    # Finally, some centering text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y,
                             libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))


# TODO Delete in favor of a Screen
def _render_all(ui, game):
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
        libtcod.console_print_ex(ui.panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    # Show player's stats
    _render_ui_bar(ui.panel, 1, 1, BAR_WIDTH, 'HP', game.player.hp,
                   game.player.max_hp, libtcod.light_red, libtcod.darker_red)
    _render_ui_bar(ui.panel, 1, 2, BAR_WIDTH, 'EXP', game.player.xp,
                   game.player.required_for_level_up(), libtcod.green, libtcod.darkest_green)

    # Show the dungeon level
    libtcod.console_print_ex(ui.panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Dungeon Level {}'.format(game.dungeon_level))

    # Display names of objects under the mouse
    names = _get_names_under_mouse(ui.mouse, game)
    libtcod.console_set_default_foreground(ui.panel, libtcod.light_gray)
    libtcod.console_print_ex(ui.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, names)

    # Reset the background color for next time
    libtcod.console_set_default_background(ui.panel, libtcod.black)

    # Blit the contents of the GUI panel to the root console
    libtcod.console_blit(ui.panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

    libtcod.console_flush()

