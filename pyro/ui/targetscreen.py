import tcod as libtcod
from pyro.ui.userinterface import Screen
from pyro.ui.keys import Key
from pyro.position import Position


class TargetScreen(Screen):
    def __init__(self, game_screen, item):
        Screen.__init__(self)
        self.transparent = True
        self._item = item
        self._game_screen = game_screen
        game_screen.game.log.message('Left-click to select a target, or right-click to cancel',
                                    libtcod.light_cyan)

    def handle_mouse_click(self, mouse):
        if mouse.rbutton_pressed:
            self.__cancel()
            return

        (x, y) = mouse.cx, mouse.cy

        if mouse.lbutton_pressed and self._game_screen.game.stage.map.is_xy_in_fov(x, y):
            monster = self.__monster_at(x, y)
            if monster:
                self._game_screen.current_target_actor = monster
            else:
                self._game_screen.current_target = Position(x, y)

        self.ui.pop(self._item)

    def handle_key_press(self, key):
        if key == Key.ESCAPE:
            self.__cancel()

    def __cancel(self):
        self._game_screen.game.log.message('Cancelled', libtcod.light_blue)
        self.ui.pop()

    def __monster_at(self, x, y):
        for game_object in self._game_screen.game.stage.actors:
            if game_object != self._game_screen.game.player:
                if game_object.pos.equals(x, y):
                    return game_object
        return None
