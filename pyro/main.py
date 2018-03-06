import libtcodpy as libtcod
from pyro.settings import SCREEN_HEIGHT, SCREEN_WIDTH, LIMIT_FPS
from pyro.ui.main_menu_screen import MainMenuScreen
from pyro.ui.userinterface import UserInterface
from pyro.ui.keys import Key
import pyro.ui.inputs as inputs

libtcod.console_set_custom_font('resources/terminal8x12_gs_tc.png',
                                libtcod.FONT_TYPE_GREYSCALE |
                                libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
                          'Tombs Of The Ancient Kings', False)
libtcod.sys_set_fps(LIMIT_FPS)

ui = UserInterface()

ui.bind_key(Key.ESCAPE, inputs.EXIT)
ui.bind_key(Key.ENTER, inputs.ENTER)
ui.bind_key(Key.UP, inputs.NORTH)
ui.bind_key(Key.DOWN, inputs.SOUTH)
ui.bind_key(Key.LEFT, inputs.WEST)
ui.bind_key(Key.RIGHT, inputs.EAST)
ui.bind_key(Key.C, inputs.HERO_INFO)
ui.bind_key(Key.G, inputs.PICKUP)
ui.bind_key(Key.D, inputs.DROP)
ui.bind_key(Key.I, inputs.INVENTORY)
ui.bind_key(Key.F, inputs.REST)
ui.bind_key(Key.R, inputs.CLOSE_DOOR)

ui.push(MainMenuScreen())

while ui.is_running():
    ui.refresh()
    ui.handle_input()
