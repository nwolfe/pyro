import libtcodpy as libtcod
import object as libobj
import map as libmap
import game as libgame
from settings import *


class Actions:
    def __init__(self, fov_recompute=None, player_action=None):
        self.fov_recompute = fov_recompute
        self.player_action = player_action


def move_player_or_attack(player, map, objects, messages, dx, dy, actions):
    x = player.x + dx
    y = player.y + dy
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    if target:
        player.fighter.attack(target, messages)
    else:
        player.move(map, objects, dx, dy)
        actions.player_action = 'move'
        actions.fov_recompute = True


def handle_keys(key, player, map, objects, messages, game, actions):

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt-Enter toggles fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit game
        actions.player_action = 'exit'
        return

    if game.state != 'playing':
        return

    if libtcod.KEY_UP == key.vk:
        move_player_or_attack(player, map, objects, messages, 0, -1, actions)
    elif libtcod.KEY_DOWN == key.vk:
        move_player_or_attack(player, map, objects, messages, 0, 1, actions)
    elif libtcod.KEY_LEFT == key.vk:
        move_player_or_attack(player, map, objects, messages, -1, 0, actions)
    elif libtcod.KEY_RIGHT == key.vk:
        move_player_or_attack(player, map, objects, messages, 1, 0, actions)
    else:
        actions.player_action = 'idle'


def get_names_under_mouse(mouse, objects, fov_map):
    # Return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    # Create a list with the names of all objects at the mouse's coordinates
    # and in FOV
    names = [obj.name for obj in objects
             if obj.x == x and obj.y == y and
             libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
    return ', '.join(names).capitalize()


def render_ui_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    # Render a bar (HP, experience, etc)
    bar_width = int(float(value) / maximum * total_width)

    # Render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    # Now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    # Finally, some centering text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y,
                             libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))


def render_all(con, panel, map, player, objects, messages, fov_map, mouse, actions):
    if actions.fov_recompute:
        # Recompute FOV if needed (i.e. the player moved)
        actions.fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y,
                                TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        # Set tile background colors according to FOV
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    if map[x][y].explored:
                        color = COLOR_DARK_WALL if wall else COLOR_DARK_GROUND
                        libtcod.console_set_char_background(con, x, y, color,
                                                            libtcod.BKGND_SET)
                else:
                    color = COLOR_LIGHT_WALL if wall else COLOR_LIGHT_GROUND
                    libtcod.console_set_char_background(con, x, y, color,
                                                        libtcod.BKGND_SET)
                    map[x][y].explored = True

    render_ordered = sorted(objects, key=lambda obj: obj.render_order)
    for object in render_ordered:
        if libtcod.map_is_in_fov(fov_map, object.x, object.y):
            object.draw(con)

    # Blit the contents of the game (non-GUI) console to the root console
    libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

    # Prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # Print game messages, one line at a time
    y = 1
    for (line, color) in messages:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE,
                                 libtcod.LEFT, line)
        y += 1

    # Show player's stats
    render_ui_bar(panel, 1, 1, BAR_WIDTH, 'HP', player.fighter.hp,
                  player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)

    # Display names of objects under the mouse
    names = get_names_under_mouse(mouse, objects, fov_map)
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, names)

    # Blit the contents of the GUI panel to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)


###############################################################################
# Initialization & Main Loop                                                  #
###############################################################################

libtcod.console_set_custom_font('terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
messages = []

game = libgame.Game(state='playing')

def player_death(player):
    libgame.message(messages, 'You died!')
    game.state = 'dead'

    player.char = '%'
    player.color = libtcod.dark_red

player = libobj.Object(0, 0, '@', 'player', libtcod.white, blocks=True,
                       fighter=libobj.Fighter(hp=30, defense=2, power=5,
                                              death_fn=player_death))
objects = [player]
map = libmap.make_map(player, objects, libobj.MonsterFactory(messages))

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y,
                                   not map[x][y].block_sight,
                                   not map[x][y].blocked)

actions = Actions(fov_recompute=True)

mouse = libtcod.Mouse()
key = libtcod.Key()

libgame.message(messages, 'Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings!', libtcod.red)

while not libtcod.console_is_window_closed():
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE,
                                key, mouse)

    render_all(con, panel, map, player, objects, messages, fov_map, mouse, actions)

    libtcod.console_flush()

    for object in objects:
        object.clear(con)

    handle_keys(key, player, map, objects, messages, game, actions)

    if actions.player_action == 'exit':
        break

    if game.state == 'playing' and actions.player_action != 'idle':
        for object in objects:
            if object.ai:
                object.ai.take_turn(map, fov_map, objects, player, messages)
