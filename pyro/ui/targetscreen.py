import tcod as libtcod
from pyro.ui.userinterface import Screen
from pyro.ui.keys import Key
from pyro.position import Position
from pyro.target import Target


class TargetScreen(Screen):
    def __init__(self, game_screen, range_=None):
        Screen.__init__(self)
        self.transparent = True
        self._game_screen = game_screen
        self._range = range_
        game_screen.game.log.message('Left-click to select a target, or right-click to cancel',
                                    libtcod.light_cyan)

    def handle_mouse_click(self, mouse):
        if mouse.rbutton_pressed:
            self.__cancel()
            return

        # Assume it's a left-click

        pos = Position(mouse.cx, mouse.cy)
        if self._range is not None:
            distance = self._game_screen.game.player.pos.distance_to(pos)
            if distance > self._range:
                self._game_screen.game.log.message(
                    'Out of range. Select again.', libtcod.light_blue)
                return

        target = Target(position=pos)
        if self._game_screen.game.stage.map.is_in_fov(pos):
            monster = self.__monster_at(pos)
            target.actor = monster

        self.ui.pop(target)

    def handle_key_press(self, key):
        if key == Key.ESCAPE:
            self.__cancel()

    def handle_mouse_move(self, mouse):
        self.dirty()

    def __cancel(self):
        self._game_screen.game.log.message('Cancelled', libtcod.light_blue)
        self.ui.pop()

    def __monster_at(self, pos):
        for game_object in self._game_screen.game.stage.actors:
            if game_object != self._game_screen.game.player:
                if game_object.pos == pos:
                    return game_object
        return None
