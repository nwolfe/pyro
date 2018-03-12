from pyro.ui.userinterface import Screen, draw_menu, Key
from pyro.settings import CONTROL_SCREEN_WIDTH
import pyro.ui.inputs as inputs


class ControlScreen(Screen):
    def render(self):
        ls = [
            inputs.NORTH,
            inputs.SOUTH,
            inputs.EAST,
            inputs.WEST,
            inputs.EXIT,
            inputs.ENTER,
            inputs.INVENTORY,
            inputs.PICKUP,
            inputs.DROP,
            inputs.HERO_INFO,
            inputs.REST,
            inputs.CLOSE_DOOR
        ]
        rs = []
        for l in ls:
            rs.append(self._binding_for(l))
        draw_menu(self.ui.console, '-- Key Bindings --', rs,
                  CONTROL_SCREEN_WIDTH, None, ls, '%10s: %s')

    def handle_key_press(self, key):
        if Key.ESCAPE == key:
            self.ui.pop()

    def _binding_for(self, input_):
        for key, value in self.ui.keybindings.iteritems():
            if input_ == value:
                return key
        return None
