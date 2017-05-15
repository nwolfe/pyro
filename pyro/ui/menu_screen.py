import tcod as libtcod
from pyro.ui.userinterface import Screen
from pyro.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class MenuSelection:
    def __init__(self, selection):
        self.selection = selection


class MenuScreen(Screen):
    def __init__(self, header, menu_options, width):
        Screen.__init__(self)
        self.header = header
        self.options = menu_options
        self.width = width

    def handle_key_press(self, key):
        # Convert ASCII code to an index; if it corresponds to an option, return it
        selection = None
        index = key.ord - ord('a')
        if 0 <= index < len(self.options):
            selection = MenuSelection(index)
        self.ui.pop(selection)

    def render(self):
        if len(self.options) > 26:
            raise ValueError('Cannot have a menu with more than 26 options.')

        # Calculate total height for header (after auto-wrap),
        # and one line per option
        if self.header == '':
            header_height = 0
        else:
            header_height = libtcod.console_get_height_rect(self.ui.console, 0, 0, self.width,
                                                            SCREEN_HEIGHT, self.header)
        height = len(self.options) + header_height

        # Create an off-screen console that represents the menu's window
        window = libtcod.console_new(self.width, height)

        # Print the header, with auto-wrap
        libtcod.console_set_default_foreground(window, libtcod.white)
        libtcod.console_print_rect_ex(window, 0, 0, self.width, height,
                                      libtcod.BKGND_NONE, libtcod.LEFT, self.header)

        # Print all the options
        y = header_height
        letter_index = ord('a')
        for option in self.options:
            text = '({0}) {1}'.format(chr(letter_index), option)
            libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE,
                                     libtcod.LEFT, text)
            y += 1
            letter_index += 1

        # Blit the contents of the menu window to the root console
        x = SCREEN_WIDTH/2 - self.width/2
        y = SCREEN_HEIGHT/2 - height/2
        libtcod.console_blit(window, 0, 0, self.width, height, 0, x, y, 1.0, 0.7)

        # Present the root console to the player and wait for a key press
        libtcod.console_flush()
