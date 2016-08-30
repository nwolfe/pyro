import libtcodpy as libtcod
import object as libobj
import map as libmap
import game as libgame
import ui as libui
import shelve
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


def handle_keys(game):
    if game.key.vk == libtcod.KEY_ENTER and game.key.lalt:
        # Alt-Enter toggles fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif game.key.vk == libtcod.KEY_ESCAPE:
        # Exit game
        return (False, 'exit')

    if game.state != 'playing':
        return (False, None)

    key_char = chr(game.key.c)

    if libtcod.KEY_UP == game.key.vk:
        return move_player_or_attack(0, -1, game)
    elif libtcod.KEY_DOWN == game.key.vk:
        return move_player_or_attack(0, 1, game)
    elif libtcod.KEY_LEFT == game.key.vk:
        return move_player_or_attack(-1, 0, game)
    elif libtcod.KEY_RIGHT == game.key.vk:
        return move_player_or_attack(1, 0, game)
    elif 'g' == key_char:
        # Pick up an item; look for one in the player's tile
        for object in game.objects:
            if object.item:
                if object.x == game.player.x and object.y == game.player.y:
                    object.item.pick_up(game)
                    break
        return (False, None)
    elif 'i' == key_char:
        # Show the inventory
        msg = 'Select an item to use it, or any other key to cancel.\n'
        selected_item = libui.inventory_menu(game.console, game.inventory, msg)
        if selected_item:
            selected_item.use(game)
        return (False, None)
    elif 'd' == key_char:
        # Show the inventory; if an item is selected, drop it
        msg = 'Select an item to drop it, or any other key to cancel.\n'
        selected_item = libui.inventory_menu(game.console, game.inventory, msg)
        if selected_item:
            selected_item.drop(game)
        return (False, None)
    elif '>' == key_char:
        # Go down the stairs to the next level
        if game.stairs.x == game.player.x and game.stairs.y == game.player.y:
            next_dungeon_level(game)
            libtcod.console_clear(game.console)
        return (True, None)
    else:
        return (False, 'idle')


def player_death(player, game):
    game.message('You died!')
    game.state = 'dead'

    player.char = '%'
    player.color = libtcod.dark_red


def make_fov_map(map):
    # Create the FOV map according to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y,
                                       not map[x][y].block_sight,
                                       not map[x][y].blocked)
    return fov_map


def new_game(console, panel):
    # Create the player
    fighter_comp = libobj.Fighter(hp=30, defense=2, power=5,
                                  death_fn=player_death)
    player = libobj.Object(0, 0, '@', 'player', libtcod.white, blocks=True,
                           fighter=fighter_comp)

    # Generate map (not drawn to the screen yet)
    (map, objects, stairs) = libmap.make_map(player)
    fov_map = make_fov_map(map)

    mouse = libtcod.Mouse()
    key = libtcod.Key()

    inventory = []
    messages = []

    game = libgame.Game('playing', console, panel, mouse, key, map, fov_map,
                        objects, stairs, player, inventory, messages)

    m = 'Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings!'
    game.message(m, libtcod.red)

    return game


def next_dungeon_level(game):
    # Advance to the next level
    # Heal the player by 50%
    game.message('You take a moment to rest, and recover your strength.',
                 libtcod.light_violet)
    game.player.fighter.heal(game.player.fighter.max_hp / 2)

    msg = 'After a rare moment of peace, you descend deeper into the heart '
    msg += 'of the dungeon...'
    game.message(msg, libtcod.red)
    game.dungeon_level += 1

    (map, objects, stairs) = libmap.make_map(game.player)
    fov_map = make_fov_map(map)

    game.map = map
    game.fov_map = fov_map
    game.objects = objects
    game.stairs = stairs


def play_game(game):
    fov_recompute = True
    libtcod.console_clear(game.console)
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS |
                                    libtcod.EVENT_MOUSE, game.key, game.mouse)

        libui.render_all(game, fov_recompute)

        libtcod.console_flush()

        for object in game.objects:
            object.clear(game.console)

        (fov_recompute, player_action) = handle_keys(game)

        if player_action == 'exit':
            save_game(game)
            break

        if game.state == 'playing' and player_action != 'idle':
            for object in game.objects:
                if object.ai:
                    object.ai.take_turn(game)


def save_game(game):
    # Open an empty shelve (possibly overwriting an old one) to write the data
    file = shelve.open('savegame', 'n')
    file['map'] = game.map
    file['objects'] = game.objects
    file['player_index'] = game.objects.index(game.player)
    file['inventory'] = game.inventory
    file['messages'] = game.messages
    file['state'] = game.state
    file['stairs_index'] = game.objects.index(game.stairs)
    file['dungeon_level'] = game.dungeon_level
    file.close()


def load_game(console, panel):
    # Open the previously saved shelve and load the game data
    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]
    inventory = file['inventory']
    messages = file['messages']
    state = file['state']
    stairs = objects[file['stairs_index']]
    dungeon_level = file['dungeon_level']
    file.close()

    fov_map = make_fov_map(map)
    mouse = libtcod.Mouse()
    key = libtcod.Key()

    return libgame.Game(state, console, panel, mouse, key, map, fov_map,
                        objects, stairs, player, inventory, messages,
                        dungeon_level)


def main_menu(console, panel):
    background = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        # Show the image at twice the regular console resolution
        libtcod.image_blit_2x(background, 0, 0, 0)

        # Show the game's title and credits
        libtcod.console_set_default_foreground(console, libtcod.light_yellow)
        libtcod.console_print_ex(console, SCREEN_WIDTH/2, (SCREEN_HEIGHT/2)-4,
                                 libtcod.BKGND_NONE, libtcod.CENTER,
                                 'TOMBS OF THE ANCIENT KINGS')
        libtcod.console_print_ex(console, SCREEN_WIDTH/2, SCREEN_HEIGHT-2,
                                 libtcod.BKGND_NONE, libtcod.CENTER,
                                 'By N. Wolfe')

        # Show options and wait for the player's choice
        options = ['Play a new game', 'Continue last game', 'Quit']
        choice = libui.menu(console, '', options, 24)

        if choice == 0:
            # New game
            game = new_game(console, panel)
            play_game(game)
        elif choice == 1:
            # Load last game
            try:
                game = load_game(console, panel)
                play_game(game)
            except:
                libui.messagebox('\n No saved game to load.\n', 24)
                continue
        elif choice == 2:
            # Quit
            break


###############################################################################
# Initialization & Main Loop                                                  #
###############################################################################

libtcod.console_set_custom_font('terminal8x12_gs_tc.png',
                                libtcod.FONT_TYPE_GREYSCALE |
                                libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
                          'Tombs Of The Ancient Kings', False)
libtcod.sys_set_fps(LIMIT_FPS)

console = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

main_menu(console, panel)
