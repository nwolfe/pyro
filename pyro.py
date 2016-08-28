import libtcodpy as libtcod
import object as libobj
import map as libmap
import game as libgame
import ui as libui
from settings import *


def move_player_or_attack(dx, dy, game):
    x = game.player.x + dx
    y = game.player.y + dy
    target = None
    for object in game.objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    if target:
        game.player.fighter.attack(target, game)
        return (False, None)
    else:
        game.player.move(game.map, game.objects, dx, dy)
        return (True, 'move')


def handle_keys(key, con, game):
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt-Enter toggles fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit game
        return (False, 'exit')

    if game.state != 'playing':
        return (False, None)

    if libtcod.KEY_UP == key.vk:
        return move_player_or_attack(0, -1, game)
    elif libtcod.KEY_DOWN == key.vk:
        return move_player_or_attack(0, 1, game)
    elif libtcod.KEY_LEFT == key.vk:
        return move_player_or_attack(-1, 0, game)
    elif libtcod.KEY_RIGHT == key.vk:
        return move_player_or_attack(1, 0, game)
    elif 'g' == chr(key.c):
        # Pick up an item; look for one in the player's tile
        for object in game.objects:
            if object.item:
                if object.x == game.player.x and object.y == game.player.y:
                    object.item.pick_up(game)
                    break
        return (False, None)
    elif 'i' == chr(key.c):
        # Show the inventory
        msg = 'Select an item to use it, or any other key to cancel.\n'
        selected_item = libui.inventory_menu(con, game.inventory, msg)
        if selected_item:
            selected_item.use(game)
        return (False, None)
    else:
        return (False, 'idle')


def player_death(player, game):
    game.message('You died!')
    game.state = 'dead'

    player.char = '%'
    player.color = libtcod.dark_red


###############################################################################
# Initialization & Main Loop                                                  #
###############################################################################

libtcod.console_set_custom_font('terminal8x12_gs_tc.png',
                                libtcod.FONT_TYPE_GREYSCALE |
                                libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
                          'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)

con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
messages = []
inventory = []
player = libobj.Object(0, 0, '@', 'player', libtcod.white, blocks=True,
                       fighter=libobj.Fighter(hp=30, defense=2, power=5,
                                              death_fn=player_death))
objects = [player]
map = libmap.make_map(player, objects)

fov_recompute = True
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y,
                                   not map[x][y].block_sight,
                                   not map[x][y].blocked)

game = libgame.Game('playing', map, fov_map,
                    objects, player, inventory, messages)

mouse = libtcod.Mouse()
key = libtcod.Key()

msg = 'Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings!'
game.message(msg, libtcod.red)

while not libtcod.console_is_window_closed():
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE,
                                key, mouse)

    libui.render_all(con, panel, game, mouse, fov_recompute)

    libtcod.console_flush()

    for object in game.objects:
        object.clear(con)

    (fov_recompute, player_action) = handle_keys(key, con, game)

    if player_action == 'exit':
        break

    if game.state == 'playing' and player_action != 'idle':
        for object in game.objects:
            if object.ai:
                object.ai.take_turn(game)
