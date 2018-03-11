import libtcodpy as libtcod
from pyro.ui.userinterface import Screen, draw_menu, Key


_BACKGROUND_IMAGE = libtcod.image_load('resources/menu_background.png')


class PauseScreen(Screen):
    def handle_key_press(self, key):
        index = key.ord - ord('a')
        if index == 0 or key == Key.ESCAPE:
            # Continue
            self.ui.pop()
        elif index == 1:
            # New Game
            self.ui.pop(index)
        elif index == 2:
            # Quit
            self.ui.pop(index)

    def render(self):
        libtcod.image_blit_2x(_BACKGROUND_IMAGE, 0, 0, 0)
        options = ['Continue', 'New Game', 'Quit']
        draw_menu(self.ui.console, '', options, 24)
