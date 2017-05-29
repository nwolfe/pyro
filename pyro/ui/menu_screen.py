from collections import namedtuple
from pyro.ui.userinterface import Screen, draw_menu


MenuSelection = namedtuple('MenuSelection', 'choice index')


class MenuScreen(Screen):
    def __init__(self, header, menu_options, width, empty_text=None, require_selection=False):
        Screen.__init__(self)
        self.transparent = True
        self._header = header
        self._options = menu_options
        self._width = width
        self._empty_text = empty_text
        self._selection_required = require_selection

    def handle_key_press(self, key):
        # Convert ASCII code to an index; if it corresponds to an option, return it
        index = key.ord - ord('a')
        if 0 <= index < len(self._options):
            self.ui.pop(MenuSelection(self._options[index], index))
        elif not self._selection_required:
            self.ui.pop()

    def render(self):
        draw_menu(self.ui.console, self._header, self._options, self._width, self._empty_text)
