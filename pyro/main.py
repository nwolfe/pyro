import shelve
import libtcodpy as libtcod
from pyro.objects import GameObjectFactory
from pyro.map import make_map
from pyro.game import Game
from pyro.ui import UserInterface, render_all, messagebox, menu, inventory_menu
from pyro.gameobject import GameObject
from pyro.components.ai import AI
from pyro.components.fighter import Fighter
from pyro.components.experience import Experience
from pyro.components.item import Item, Inventory, Equipment
from pyro.components.door import Door
from pyro.components.grass import Grass
from pyro.components.projectile import Projectile
from pyro.settings import *


def move_player_or_attack(dx, dy, game):
    x = game.player.x + dx
    y = game.player.y + dy
    target = None
    for game_object in game.objects:
        if game_object.component(Fighter):
            if game_object.x == x and game_object.y == y:
                target = game_object
                break

    if target:
        game.player.component(Fighter).attack(target)
        return False, 'attack'
    else:
        door = None
        grass = None
        for game_object in game.objects:
            if game_object.component(Door):
                if game_object.x == x and game_object.y == y:
                    door = game_object.component(Door)
            elif game_object.component(Grass):
                if game_object.x == x and game_object.y == y:
                    if not game_object.component(Grass).is_crushed:
                        grass = game_object.component(Grass)

            if door and grass:
                break

        moved = game.player.move(dx, dy)
        if moved:
            if grass:
                grass.crush()
        else:
            if door:
                door.open()
        return True, 'move'


def close_nearest_door(game):
    x = game.player.x
    y = game.player.y
    for game_object in game.objects:
        if game_object.component(Door):
            close_x = (game_object.x == x or game_object.x == x-1 or game_object.x == x+1)
            close_y = (game_object.y == y or game_object.y == y-1 or game_object.y == y+1)
            player_on_door = (game_object.x == x and game_object.y == y)
            if close_x and close_y and not player_on_door:
                game_object.component(Door).close()
                break


def show_character_info(console, game):
    msg = """Character Information

Level: {0}
Experience: {1}
Next Level: {2}

Current HP: {3}
Maximum HP: {4}
Attack: {5}
Defense: {6}
"""
    exp = game.player.component(Experience)
    fighter = game.player.component(Fighter)
    msg = msg.format(exp.level,
                     exp.xp,
                     exp.required_for_level_up(),
                     fighter.hp,
                     fighter.max_hp(),
                     fighter.power(),
                     fighter.defense())
    messagebox(console, msg, CHARACTER_SCREEN_WIDTH)


def handle_keys(ui, game, object_factory):
    if ui.keyboard.vk == libtcod.KEY_ENTER and ui.keyboard.lalt:
        # Alt-Enter toggles fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif ui.keyboard.vk == libtcod.KEY_ESCAPE:
        # Exit game
        return False, 'exit'

    if game.state != 'playing':
        return False, None

    key_char = chr(ui.keyboard.c)

    if libtcod.KEY_UP == ui.keyboard.vk:
        return move_player_or_attack(0, -1, game)
    elif libtcod.KEY_DOWN == ui.keyboard.vk:
        return move_player_or_attack(0, 1, game)
    elif libtcod.KEY_LEFT == ui.keyboard.vk:
        return move_player_or_attack(-1, 0, game)
    elif libtcod.KEY_RIGHT == ui.keyboard.vk:
        return move_player_or_attack(1, 0, game)
    elif key_char == 'q': # up-left
        return move_player_or_attack(-1, -1, game)
    elif key_char == 'e': # up-right
        return move_player_or_attack(1, -1, game)
    elif key_char == 'z': # down-left
        return move_player_or_attack(-1, 1, game)
    elif key_char == 'x': # down-right
        return move_player_or_attack(1, 1, game)
    elif key_char == 'f':
        # Don't move, let the monsters come to you
        return False, None
    elif key_char == 'g':
        # Pick up an item; look for one in the player's tile
        for game_object in game.objects:
            item = game_object.component(Item)
            if item:
                if game_object.x == game.player.x and game_object.y == game.player.y:
                    item.pick_up(game.player)
                    break
        return False, None
    elif key_char == 'i':
        # Show the inventory
        msg = 'Select an item to use it, or any other key to cancel.\n'
        inventory = game.player.component(Inventory).items
        selected_item = inventory_menu(ui.console, inventory, msg)
        if selected_item:
            selected_item.use(ui)
        return False, None
    elif key_char == 'd':
        # Show the inventory; if an item is selected, drop it
        msg = 'Select an item to drop it, or any other key to cancel.\n'
        inventory = game.player.component(Inventory).items
        selected_item = inventory_menu(ui.console, inventory, msg)
        if selected_item:
            selected_item.drop()
        return False, None
    elif key_char == '>':
        # Go down the stairs to the next level
        if game.stairs.x == game.player.x and game.stairs.y == game.player.y:
            next_dungeon_level(game, object_factory)
            libtcod.console_clear(ui.console)
        return True, None
    elif key_char == 'c':
        show_character_info(ui.console, game)
        return False, None
    elif key_char == 'r':
        close_nearest_door(game)
        return True, None
    else:
        return False, 'idle'


def player_death(player, game):
    game.message('You died!')
    game.state = 'dead'

    player.glyph = '%'
    player.color = libtcod.dark_red


def make_fov_map(game_map):
    # Create the FOV map according to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y,
                                       not game_map[x][y].block_sight,
                                       not game_map[x][y].blocked)
    return fov_map


def check_player_level_up(game, console):
    player = game.player
    exp = player.component(Experience)

    # See if the player's XP is enough to level up
    if exp.can_level_up():
        return

    # Ding! Level up!
    exp.level_up()
    msg = 'Your battle skills grow stronger! You reached level {}!'
    game.message(msg.format(exp.level), libtcod.yellow)

    choice = None
    while choice is None:
        fighter = player.component(Fighter)
        options = ['Constitution (+20 HP, from {})'.format(fighter.base_max_hp),
                   'Strength (+1 attack, from {})'.format(fighter.base_power),
                   'Agility (+1 defense, from {})'.format(fighter.base_defense)]
        choice = menu(console, 'Level up! Choose a stat to raise:\n', options, LEVEL_SCREEN_WIDTH)
        if choice == 0:
            fighter.base_max_hp += 20
            fighter.hp += 20
        elif choice == 1:
            fighter.base_power += 1
        elif choice == 2:
            fighter.base_defense += 1


def new_game(object_factory):
    # Create the player
    exp_comp = Experience(xp=0, level=1)
    fighter_comp = Fighter(hp=100, defense=1, power=2, death_fn=player_death)
    player_inventory = Inventory(items=[])
    player = GameObject(0, 0, '@', 'player', libtcod.white, blocks=True,
                        components={Fighter: fighter_comp,
                                    Experience: exp_comp,
                                    Inventory: player_inventory})

    # Generate map (not drawn to the screen yet)
    dungeon_level = 1
    (game_map, objects, stairs) = make_map(player, dungeon_level, object_factory)
    fov_map = make_fov_map(game_map)

    messages = []

    game = Game('playing', game_map, fov_map, objects, stairs,
                player, messages, dungeon_level)

    # Initial equipment: a dagger and scroll of lightning bolt
    dagger = object_factory.new_item('Dagger')
    dagger.component(Equipment).item_owner = player
    dagger.component(Equipment).is_equipped = True
    player_inventory.items.append(dagger)
    dagger.game = game

    spell = object_factory.new_item('Scroll Of Lightning Bolt')
    spell.component(Item).item_owner = player
    player_inventory.items.append(spell)
    spell.game = game

    spell = object_factory.new_item('Scroll Of Fireball')
    spell.component(Item).item_owner = player
    player_inventory.items.append(spell)
    spell.game = game

    m = 'Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings!'
    game.message(m, libtcod.red)

    return game


def next_dungeon_level(game, object_factory):
    # Advance to the next level
    # Heal the player by 50%
    game.message('You take a moment to rest, and recover your strength.',
                 libtcod.light_violet)
    fighter = game.player.component(Fighter)
    fighter.heal(fighter.max_hp() / 2)

    msg = 'After a rare moment of peace, you descend deeper into the heart '
    msg += 'of the dungeon...'
    game.message(msg, libtcod.red)
    game.dungeon_level += 1

    (game_map, objects, stairs) = make_map(game.player, game.dungeon_level, object_factory)
    fov_map = make_fov_map(game_map)

    game.game_map = game_map
    game.fov_map = fov_map
    game.objects = objects
    game.stairs = stairs

    for game_object in game.objects:
        game_object.game = game


def update_projectiles(game):
    projectiles_found = False
    for game_object in game.objects:
        projectile = game_object.component(Projectile)
        if projectile:
            projectile.tick()
            projectiles_found = True
    return projectiles_found


def play_game(game, ui, object_factory):
    for game_object in game.objects:
        game_object.game = game

    fov_recompute = True
    libtcod.console_clear(ui.console)
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS |
                                    libtcod.EVENT_MOUSE, ui.keyboard, ui.mouse)

        render_all(ui, game, fov_recompute)

        libtcod.console_flush()

        check_player_level_up(game, ui.console)

        for game_object in game.objects:
            game_object.clear(ui.console)

        if update_projectiles(game):
            continue

        (fov_recompute, player_action) = handle_keys(ui, game, object_factory)

        if player_action == 'exit':
            save_game(game)
            break

        if game.state == 'playing' and player_action != 'idle':
            for game_object in game.objects:
                ai = game_object.component(AI)
                if ai:
                    ai.take_turn()


def save_game(game):
    # Open an empty shelve (possibly overwriting an old one) to write the data
    save_file = shelve.open('savegame', 'n')
    save_file['map'] = game.game_map
    save_file['objects'] = game.objects
    save_file['player_index'] = game.objects.index(game.player)
    save_file['messages'] = game.messages
    save_file['state'] = game.state
    save_file['stairs_index'] = game.objects.index(game.stairs)
    save_file['dungeon_level'] = game.dungeon_level
    save_file.close()


def load_game():
    # Open the previously saved shelve and load the game data
    save_file = shelve.open('savegame', 'r')
    game_map = save_file['map']
    objects = save_file['objects']
    player = objects[save_file['player_index']]
    messages = save_file['messages']
    state = save_file['state']
    stairs = objects[save_file['stairs_index']]
    dungeon_level = save_file['dungeon_level']
    save_file.close()

    fov_map = make_fov_map(game_map)

    return Game(state, game_map, fov_map, objects, stairs, player, messages, dungeon_level)


def main_menu(ui):
    background = libtcod.image_load('menu_background.png')

    object_factory = GameObjectFactory()
    object_factory.load_templates(monster_file='resources/monsters.json',
                                  item_file='resources/items.json')

    while not libtcod.console_is_window_closed():
        # Show the image at twice the regular console resolution
        libtcod.image_blit_2x(background, 0, 0, 0)

        # Show the game's title and credits
        libtcod.console_set_default_foreground(ui.console, libtcod.light_yellow)

        # Show options and wait for the player's choice
        options = ['Play a new game', 'Continue last game', 'Quit']
        choice = menu(ui.console, '', options, 24)

        if choice == 0:
            # New game
            game = new_game(object_factory)
            play_game(game, ui, object_factory)
        elif choice == 1:
            # Load last game
            try:
                game = load_game()
                play_game(game, ui, object_factory)
            except:
                messagebox(ui.console, '\n No saved game to load.\n', 24)
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

keyboard = libtcod.Key()
mouse = libtcod.Mouse()
console = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
ui = UserInterface(keyboard, mouse, console, panel)

main_menu(ui)
