import tcod as libtcod
from pyro.settings import SCREEN_HEIGHT, SCREEN_WIDTH, LIMIT_FPS
from pyro.ui.main_menu_screen import MainMenuScreen
from pyro.ui.userinterface import UserInterface
from pyro.ui.keys import Key
from pyro.ui.inputs import Input

libtcod.console_set_custom_font('resources/terminal8x12_gs_tc.png',
                                libtcod.FONT_TYPE_GREYSCALE |
                                libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
                          'Tombs Of The Ancient Kings', False)
libtcod.sys_set_fps(LIMIT_FPS)

ui = UserInterface()

ui.bind_key(Key.ESCAPE, Input.EXIT)
ui.bind_key(Key.ENTER, Input.ENTER)
ui.bind_key(Key.UP, Input.NORTH)
ui.bind_key(Key.DOWN, Input.SOUTH)
ui.bind_key(Key.LEFT, Input.WEST)
ui.bind_key(Key.RIGHT, Input.EAST)
ui.bind_key(Key.C, Input.HERO_INFO)
ui.bind_key(Key.G, Input.PICKUP)
ui.bind_key(Key.D, Input.DROP)
ui.bind_key(Key.I, Input.INVENTORY)
ui.bind_key(Key.F, Input.REST)
ui.bind_key(Key.R, Input.CLOSE_DOOR)

ui.push(MainMenuScreen())

while ui.is_running():
    ui.refresh()
    ui.handle_input()
