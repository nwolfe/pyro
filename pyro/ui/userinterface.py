import libtcodpy as libtcod
from pyro.settings import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT
from pyro.settings import PANEL_HEIGHT
from pyro.ui.keys import key_for_int, Key


# Game loop:
#     while ui.is_running():
#         ui.refresh()
#         ui.handle_input()
class UserInterface:
    def __init__(self):
        self.screens = []
        self.keybindings = {}
        self._keyboard = libtcod.Key()
        self.mouse = libtcod.Mouse()
        self.console = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
        self.panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
        self._dirty = True

    def dirty(self):
        self._dirty = True

    def bind_key(self, key, input_):
        self.keybindings[key] = input_

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
        if self._dirty:
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

        self._dirty = False
        libtcod.console_flush()

    def handle_input(self):
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE,
                                    self._keyboard, self.mouse)
        screen = self.top_screen()
        self._handle_keypress(screen)
        if self.mouse.lbutton_pressed or self.mouse.rbutton_pressed:
            screen.handle_mouse_click(self.mouse)
        if self.mouse.dx != 0 or self.mouse.dy != 0:
            screen.handle_mouse_move(self.mouse)

    def top_screen(self):
        return self.screens[len(self.screens) - 1]

    def is_running(self):
        return not libtcod.console_is_window_closed() and len(self.screens) > 0

    def _handle_keypress(self, screen):
        key = self._check_for_keypress()
        if key:
            if key in self.keybindings:
                if screen.handle_input(self.keybindings[key]):
                    return
            screen.handle_key_press(key)

    def _check_for_keypress(self):
        vk = self._keyboard.vk
        if libtcod.KEY_NONE == vk:
            return None

        if libtcod.KEY_LEFT == vk:
            result = Key.LEFT
        elif libtcod.KEY_RIGHT == vk:
            result = Key.RIGHT
        elif libtcod.KEY_UP == vk:
            result = Key.UP
        elif libtcod.KEY_DOWN == vk:
            result = Key.DOWN
        elif libtcod.KEY_ESCAPE == vk:
            result = Key.ESCAPE
        elif libtcod.KEY_ENTER == vk:
            result = Key.ENTER
        else:
            result = key_for_int(self._keyboard.c)
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

    def dirty(self):
        if self.ui:
            self.ui.dirty()

    def handle_input(self, input_):
        return False

    def handle_key_press(self, key):
        pass

    def handle_mouse_click(self, mouse):
        pass

    def handle_mouse_move(self, mouse):
        pass


# TODO This seems inappropriate in this userinterface module.
# Where should this function live?
def draw_menu(console, header, options, width,
              empty_text=None, keys=None, format_=None):
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
    if format_:
        fmt = format_
    else:
        fmt = '(%s) %s'
    y = header_height
    letter_index = ord('a')
    for i in range(len(options)):
        if keys:
            key = keys[i]
        else:
            key = chr(letter_index)
        text = fmt % (key, options[i])
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # Blit the contents of the menu window to the root console
    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
