import libtcodpy as libtcod
from pyro import objects
from pyro.engine.game import Game
from pyro.map import make_map
from pyro.ui.game_screen import GameScreen
from pyro.ui.controlscreen import ControlScreen
from pyro.ui.userinterface import Screen, draw_menu


_BACKGROUND_IMAGE = libtcod.image_load('resources/menu_background.png')


class MainMenuScreen(Screen):
    def handle_key_press(self, key):
        index = key.ord - ord('a')
        if index == 0:
            self.ui.push(GameScreen(_new_game()))
        elif index == 1:
            self.ui.push(ControlScreen())
        elif index == 2:
            self.ui.pop()

    def render(self):
        # Show the image at twice the regular console resolution
        libtcod.image_blit_2x(_BACKGROUND_IMAGE, 0, 0, 0)
        draw_menu(self.ui.console, '', ['New Game', 'Controls', 'Quit'], 24)

    def activate(self, result=None, tag=None, data=None):
        # This index comes from PauseScreen
        if result == 1:
            # New Game
            self.ui.push(GameScreen(_new_game()))
        elif result == 3:
            # Quit
            self.ui.pop()


def _new_game():
    game = Game(dungeon_level=1)
    player = objects.new_player(game)
    game.player = player
    make_map(game)

    game.log.error('Prepare to perish!')

    return game
