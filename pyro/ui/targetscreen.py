import tcod as libtcod
from collections import namedtuple
from pyro.ui.userinterface import Screen
from pyro.ui.keys import Key
from pyro.position import Position


TargetSelection = namedtuple('TargetSelection', 'actor position')


class TargetScreen(Screen):
    def __init__(self, game_screen):
        Screen.__init__(self)
        self.transparent = True
        self._game_screen = game_screen
        game_screen.game.log.message('Left-click to select a target, or right-click to cancel',
                                    libtcod.light_cyan)

    def handle_mouse_click(self, mouse):
        if mouse.rbutton_pressed:
            self.__cancel()
            return

        pos = Position(mouse.cx, mouse.cy)
        if mouse.lbutton_pressed and self._game_screen.game.stage.map.is_in_fov(pos):
            monster = self.__monster_at(pos)
            self.ui.pop(TargetSelection(monster, pos))
        else:
            self.ui.pop()

    def handle_key_press(self, key):
        if key == Key.ESCAPE:
            self.__cancel()

    def __cancel(self):
        self._game_screen.game.log.message('Cancelled', libtcod.light_blue)
        self.ui.pop()

    def __monster_at(self, pos):
        for game_object in self._game_screen.game.stage.actors:
            if game_object != self._game_screen.game.player:
                if game_object.pos == pos:
                    return game_object
        return None
