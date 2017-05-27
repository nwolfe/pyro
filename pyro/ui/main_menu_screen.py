import tcod as libtcod
from pyro import objects
from pyro.engine.game import Game
from pyro.map import make_map
from pyro.ui.game_screen import GameScreen
from pyro.ui.userinterface import Screen, draw_menu


_BACKGROUND_IMAGE = libtcod.image_load('resources/menu_background.png')


class MainMenuScreen(Screen):
    def __init__(self):
        Screen.__init__(self)
        self._options = ['Play a new game', 'Quit']

    def handle_key_press(self, key):
        index = key.ord - ord('a')
        if index == 0:
            game = _new_game()
            self.ui.push(GameScreen(game))
        elif index == 1:
            self.ui.pop()

    def render(self):
        # Show the image at twice the regular console resolution
        libtcod.image_blit_2x(_BACKGROUND_IMAGE, 0, 0, 0)
        draw_menu(self.ui.console, '', self._options, 24)


def _new_game():
    game = Game(dungeon_level=1)
    player = objects.new_player(game)
    game.player = player
    make_map(game)

    game.log.messages = []
    m = 'Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings!'
    game.log.message(m, libtcod.red)

    return game
