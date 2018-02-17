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

    def bind_key(self, key, input_):
        self._keybindings[key] = input_

    def push(self, screen, tag=None, data=None):
        screen.tag = tag
        screen.data = data
        screen.bind(self)
        self.screens.append(screen)
        self.render()

    def pop(self, result=None):
        screen = self.screens.pop()
        screen.unbind()
        if len(self.screens) > 0:
            self.top_screen().activate(result, screen.tag, screen.data)
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
        screen = self.top_screen()

        key = self._check_for_keypress()
        if key:
            if key in self._keybindings:
                if screen.handle_input(self._keybindings[key]):
                    return
            screen.handle_key_press(key)

        if self.mouse.lbutton_pressed or self.mouse.rbutton_pressed:
            screen.handle_mouse_click(self.mouse)

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
        self.data = None

    def bind(self, ui):
        self.ui = ui

    def unbind(self):
        self.ui = None

    def activate(self, result=None, tag=None, data=None):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def handle_input(self, input_):
        return False

    def handle_key_press(self, key):
        pass

    def handle_mouse_click(self, mouse):
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
