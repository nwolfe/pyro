import libtcodpy as libtcod
import object as libobj
import map as libmap
from settings import *


class Actions:
    def __init__(self, fov_recompute=None, player_action=None):
        self.fov_recompute = fov_recompute
        self.player_action = player_action


class World:
    def __init__(self, map=None, player=None, objects=None, game_state=None):
        self.map = map
        self.player = player
        self.objects = objects
        self.game_state = game_state

    def move_player_or_attack(self, dx, dy, actions):
        x = self.player.x + dx
        y = self.player.y + dy
        target = None
        for object in self.objects:
            if object.fighter and object.x == x and object.y == y:
                target = object
                break

        if target:
            player.fighter.attack(target)
        else:
            self.player.move(self.map, self.objects, dx, dy)
            actions.player_action = 'move'
            actions.fov_recompute = True


def handle_keys(world, actions):
    # key = libtcod.console_check_for_keypress() # real-time
    key = libtcod.console_wait_for_keypress(True) # turn-based

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt-Enter toggles fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit game
        actions.player_action = 'exit'
        return

    if world.game_state != 'playing':
        return

    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        world.move_player_or_attack(0, -1, actions)
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        world.move_player_or_attack(0, 1, actions)
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        world.move_player_or_attack(-1, 0, actions)
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        world.move_player_or_attack(1, 0, actions)
    else:
        actions.player_action = 'idle'


def render_all(con, world, fov_map, actions):
    if actions.fov_recompute:
        # Recompute FOV if needed (i.e. the player moved)
        actions.fov_recompute = False
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

    render_ordered = sorted(world.objects, key=lambda obj: obj.render_order)
    for object in render_ordered:
        if libtcod.map_is_in_fov(fov_map, object.x, object.y):
            object.draw(con)

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    # Show player's stats
    libtcod.console_set_default_foreground(con, libtcod.white)
    libtcod.console_print_ex(con, 1, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE,
                             libtcod.LEFT, 'HP {0}/{1}'.format(
                                 player.fighter.hp, player.fighter.max_hp))



###############################################################################
# Initialization & Main Loop                                                  #
###############################################################################

libtcod.console_set_custom_font('terminal8x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

player = libobj.Object(0, 0, '@', 'player', libtcod.white, blocks=True,
                       fighter=libobj.Fighter(hp=30, defense=2, power=5))
objects = [player]
map = libmap.make_map(player, objects)
world = World(map=map, player=player, objects=objects, game_state='playing')

def player_death(player):
    print 'You died!'
    world.game_state = 'dead'

    player.char = '%'
    player.color = libtcod.dark_red

player.fighter.death_fn = player_death

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y,
                                   not world.map[x][y].block_sight,
                                   not world.map[x][y].blocked)

actions = Actions(fov_recompute=True)

while not libtcod.console_is_window_closed():
    render_all(con, world, fov_map, actions)

    libtcod.console_flush()

    for object in world.objects:
        object.clear(con)

    handle_keys(world, actions)

    if actions.player_action == 'exit':
        break

    if world.game_state == 'playing' and actions.player_action != 'idle':
        for object in world.objects:
            if object.ai:
                object.ai.take_turn(world.map, fov_map, world.objects, world.player)
