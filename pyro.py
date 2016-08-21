import libtcodpy as libtcod
import object as libobj
import map as libmap
from settings import *


class World:
    def __init__(self, player):
        self.player = player
        self.objects = [player]
        self.map = libmap.make_map(self.player, self.objects)

    def move_player(self, dx, dy):
        self.player.move(self.map, self.objects, dx, dy)


def handle_keys(world, actions):
    # key = libtcod.console_check_for_keypress() # real-time
    key = libtcod.console_wait_for_keypress(True) # turn-based

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt-Enter toggles fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit game
        actions['exit'] = True
        return

    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        world.move_player(0, -1)
        actions['fov_recompute'] = True
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        world.move_player(0, 1)
        actions['fov_recompute'] = True
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        world.move_player(-1, 0)
        actions['fov_recompute'] = True
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        world.move_player(1, 0)
        actions['fov_recompute'] = True


def render_all(con, world, fov_map, actions):
    if 'fov_recompute' in actions:
        # Recompute FOV if needed (i.e. the player moved)
        actions['fov_recompute'] = False
        libtcod.map_compute_fov(fov_map, player.x, player.y,
                                TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        # Set tile background colors according to FOV
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = world.map[x][y].block_sight
                if not visible:
                    if world.map[x][y].explored:
                        color = COLOR_DARK_WALL if wall else COLOR_DARK_GROUND
                        libtcod.console_set_char_background(con, x, y, color,
                                                            libtcod.BKGND_SET)
                else:
                    color = COLOR_LIGHT_WALL if wall else COLOR_LIGHT_GROUND
                    libtcod.console_set_char_background(con, x, y, color,
                                                        libtcod.BKGND_SET)
                    world.map[x][y].explored = True

    for object in world.objects:
        if libtcod.map_is_in_fov(fov_map, object.x, object.y):
            object.draw(con)

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


###############################################################################
# Initialization & Main Loop                                                  #
###############################################################################

libtcod.console_set_custom_font('terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

player = libobj.Object(0, 0, '@', 'player', libtcod.white, blocks=True)
world = World(player)

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y,
                                   not world.map[x][y].block_sight,
                                   not world.map[x][y].blocked)

actions = dict(fov_recompute = True)

while not libtcod.console_is_window_closed():
    render_all(con, world, fov_map, actions)

    libtcod.console_flush()

    for object in world.objects:
        object.clear(con)

    handle_keys(world, actions)
    if 'exit' in actions:
        break
