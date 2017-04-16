import shelve
import tcod as libtcod
from pyro.components import Experience, Item, Inventory, Equipment, Graphics
from pyro.game import Game
from pyro.map import make_map
from pyro.objects import GameObjectFactory, make_player
from pyro.settings import SCREEN_HEIGHT, SCREEN_WIDTH, INVENTORY_WIDTH, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGORITHM
from pyro.settings import COLOR_DARK_WALL, COLOR_DARK_GROUND, COLOR_LIGHT_WALL, COLOR_LIGHT_GRASS, COLOR_LIGHT_GROUND
from pyro.settings import MSG_X, BAR_WIDTH, PANEL_HEIGHT, PANEL_Y, CHARACTER_SCREEN_WIDTH, MAP_WIDTH, MAP_HEIGHT
from pyro.settings import LEVEL_UP_STAT_HP, LEVEL_UP_STAT_POWER, LEVEL_UP_STAT_DEFENSE, LEVEL_SCREEN_WIDTH, LIMIT_FPS
from pyro.ui import EngineScreen


###############################################################################
# User Interface                                                              #
###############################################################################


class UserInterface:
    def __init__(self, keyboard, mouse, console, panel):
        self.keyboard = keyboard
        self.mouse = mouse
        self.console = console
        self.panel = panel

    def render_all(self, game, fov_recompute):
        render_all(self, game, fov_recompute)


def menu(console, header, options, width):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')

    # Calculate total height for header (after auto-wrap),
    # and one line per option
    if header == '':
        header_height = 0
    else:
        header_height = libtcod.console_get_height_rect(console, 0, 0, width,
                                                        SCREEN_HEIGHT, header)
    height = len(options) + header_height

    # Create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    # Print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height,
                                  libtcod.BKGND_NONE, libtcod.LEFT, header)

    # Print all the options
    y = header_height
    letter_index = ord('a')
    for option in options:
        text = '({0}) {1}'.format(chr(letter_index), option)
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE,
                                 libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # Blit the contents of the menu window to the root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # Present the root console to the player and wait for a key press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt-Enter toggles fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    # Convert ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options):
        return index
    else:
        return None


def messagebox(console, text, width=50):
    return menu(console, text, [], width)


def inventory_menu(console, inventory, header):
    # Show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty']
    else:
        options = []
        for item in inventory:
            text = item.name
            equipment = item.component(Equipment)
            if equipment and equipment.is_equipped:
                text = '{0} (on {1})'.format(text, equipment.slot)
            options.append(text)
    selection_index = menu(console, header, options, INVENTORY_WIDTH)
    if selection_index is None or len(inventory) == 0:
        return None
    else:
        return inventory[selection_index].component(Item)


def get_names_under_mouse(mouse, objects, game_map):
    # Return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    # Create a list with the names of all objects at the mouse's coordinates
    # and in FOV
    names = [obj.name for obj in objects
             if obj.pos.equal_to(x, y) and game_map.is_in_fov(obj.pos.x, obj.pos.y)]
    return ', '.join(names).capitalize()


def render_ui_bar(panel, x, y, total_width, name, value, maximum, bar_color,
                  back_color):
    # Render a bar (HP, experience, etc)
    bar_width = int(float(value) / maximum * total_width)

    # Render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False,
                         libtcod.BKGND_SCREEN)

    # Now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False,
                             libtcod.BKGND_SCREEN)

    # Finally, some centering text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y,
                             libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))


def render_all(ui, game, fov_recompute):
    if fov_recompute:
        # Recompute FOV if needed (i.e. the player moved)
        libtcod.map_compute_fov(game.map.fov_map, game.player.pos.x, game.player.pos.y,
                                TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGORITHM)

        # Set tile background colors according to FOV
        for y in range(game.map.height):
            for x in range(game.map.width):
                visible = game.map.is_in_fov(x, y)
                wall = game.map.movement_blocked(x, y) and game.map.vision_blocked(x, y)
                if not visible:
                    if game.map.is_explored(x, y):
                        color = COLOR_DARK_WALL if wall else COLOR_DARK_GROUND
                        libtcod.console_set_char_background(ui.console,
                                                            x, y, color,
                                                            libtcod.BKGND_SET)
                else:
                    if wall:
                        color = COLOR_LIGHT_WALL
                    elif game.map.vision_blocked(x, y):
                        color = COLOR_LIGHT_GRASS
                    else:
                        color = COLOR_LIGHT_GROUND
                    libtcod.console_set_char_background(ui.console,
                                                        x, y, color,
                                                        libtcod.BKGND_SET)
                    game.map.mark_explored(x, y)

    render_ordered = sorted(game.objects, key=lambda o: o.component(Graphics).render_order)
    for game_object in render_ordered:
        game_object.component(Graphics).draw(ui.console)

    # Blit the contents of the game (non-GUI) console to the root console
    libtcod.console_blit(ui.console, 0, 0, game.map.width, game.map.height, 0, 0, 0)

    # Prepare to render the GUI panel
    libtcod.console_set_default_background(ui.panel, libtcod.black)
    libtcod.console_clear(ui.panel)

    # Print game messages, one line at a time
    y = 1
    for (line, color) in game.messages:
        libtcod.console_set_default_foreground(ui.panel, color)
        libtcod.console_print_ex(ui.panel, MSG_X, y, libtcod.BKGND_NONE,
                                 libtcod.LEFT, line)
        y += 1

    # Show player's stats
    render_ui_bar(ui.panel, 1, 1, BAR_WIDTH, 'HP', game.player.hp,
                  game.player.max_hp, libtcod.light_red, libtcod.darker_red)
    experience = game.player.component(Experience)
    render_ui_bar(ui.panel, 1, 2, BAR_WIDTH, 'EXP', experience.xp, experience.required_for_level_up(),
                  libtcod.green, libtcod.darkest_green)

    # Show the dungeon level
    libtcod.console_print_ex(ui.panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Dungeon Level {}'.format(game.dungeon_level))

    # Display names of objects under the mouse
    names = get_names_under_mouse(ui.mouse, game.objects, game.map)
    libtcod.console_set_default_foreground(ui.panel, libtcod.light_gray)
    libtcod.console_print_ex(ui.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             names)

    # Blit the contents of the GUI panel to the root console
    libtcod.console_blit(ui.panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0,
                         PANEL_Y)

    libtcod.console_flush()
    for game_object in game.objects:
        game_object.component(Graphics).clear(ui.console)


###############################################################################
# Game Logic                                                                  #
###############################################################################


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
    msg = msg.format(exp.level,
                     exp.xp,
                     exp.required_for_level_up(),
                     game.player.hp,
                     game.player.max_hp,
                     game.player.power,
                     game.player.defense)
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

    if libtcod.KEY_UP == ui.keyboard.vk or key_char == 'k':
        # return move_player_or_attack(0, -1, game)
        pass
    elif libtcod.KEY_DOWN == ui.keyboard.vk or key_char == 'j':
        # return move_player_or_attack(0, 1, game)
        pass
    elif libtcod.KEY_LEFT == ui.keyboard.vk or key_char == 'h':
        # return move_player_or_attack(-1, 0, game)
        pass
    elif libtcod.KEY_RIGHT == ui.keyboard.vk or key_char == 'l':
        # return move_player_or_attack(1, 0, game)
        pass
    elif key_char == 'f':
        # Don't move, let the monsters come to you
        return False, None
    elif key_char == 'g':
        # Pick up an item; look for one in the player's tile
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
    elif libtcod.KEY_ENTER == ui.keyboard.vk:
        # Go down the stairs to the next level
        return True, None
    elif key_char == 'c':
        show_character_info(ui.console, game)
        return False, None
    elif key_char == 'r':
        # close_nearest_door(game)
        return True, None
    else:
        return False, 'idle'


def check_player_level_up(game, console):
    player = game.player
    exp = player.component(Experience)

    # See if the player's XP is enough to level up
    if not exp.can_level_up():
        return

    # Ding! Level up!
    exp.level_up()
    msg = 'Your battle skills grow stronger! You reached level {}!'
    game.message(msg.format(exp.level), libtcod.yellow)

    choice = None
    while choice is None:
        options = ['Constitution (+{0} HP, from {1})'.format(LEVEL_UP_STAT_HP, player.base_max_hp),
                   'Strength (+{0} attack, from {1})'.format(LEVEL_UP_STAT_POWER, player.base_power),
                   'Agility (+{0} defense, from {1})'.format(LEVEL_UP_STAT_DEFENSE, player.base_defense)]
        choice = menu(console, 'Level up! Choose a stat to raise:\n', options, LEVEL_SCREEN_WIDTH)
        if choice == 0:
            player.base_max_hp += LEVEL_UP_STAT_HP
            player.hp += LEVEL_UP_STAT_HP
        elif choice == 1:
            player.base_power += LEVEL_UP_STAT_POWER
        elif choice == 2:
            player.base_defense += LEVEL_UP_STAT_DEFENSE


def new_game(object_factory):
    # Create the player
    player = make_player()

    # Generate map (not drawn to the screen yet)
    dungeon_level = 1
    (game_map, objects) = make_map(player, dungeon_level, object_factory)

    messages = []

    game = Game('playing', game_map, objects, player, messages, dungeon_level)

    object_factory.game = game

    # Initial equipment: a dagger and scroll of lightning bolt
    dagger = object_factory.new_item('Dagger')
    dagger.component(Item).pick_up(player)

    spell = object_factory.new_item('Scroll Of Lightning Bolt')
    spell.component(Item).pick_up(player)

    spell = object_factory.new_item('Scroll Of Fireball')
    spell.component(Item).pick_up(player)

    spell = object_factory.new_item('Scroll Of Confusion')
    spell.component(Item).pick_up(player)

    game.messages = []
    m = 'Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings!'
    game.message(m, libtcod.red)

    return game


def next_dungeon_level(game, object_factory):
    # Advance to the next level
    # Heal the player by 50%
    game.message('You take a moment to rest, and recover your strength.',
                 libtcod.light_violet)
    game.player.heal(game.player.max_hp / 2)

    msg = 'After a rare moment of peace, you descend deeper into the heart '
    msg += 'of the dungeon...'
    game.message(msg, libtcod.red)
    game.dungeon_level += 1

    (game_map, objects) = make_map(game.player, game.dungeon_level, object_factory)

    game.map = game_map
    game.objects = objects

    for game_object in game.objects:
        game_object.game = game


def play_game(game, ui, object_factory):
    for game_object in game.objects:
        game_object.game = game

    libtcod.console_clear(ui.console)
    screen = EngineScreen(ui, game, object_factory)
    while not libtcod.console_is_window_closed():
        screen.render()

        check_player_level_up(game, ui.console)

        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS |
                                    libtcod.EVENT_MOUSE, ui.keyboard, ui.mouse)

        escape = screen.update()
        if escape:
            break


def save_game(game):
    # Open an empty shelve (possibly overwriting an old one) to write the data
    save_file = shelve.open('savegame', 'n')
    save_file['map'] = game.map
    save_file['objects'] = game.objects
    save_file['player_index'] = game.objects.index(game.player)
    save_file['messages'] = game.messages
    save_file['state'] = game.state
    # save_file['stairs_index'] = game.objects.index(game.stairs)
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
    # stairs = objects[save_file['stairs_index']]
    dungeon_level = save_file['dungeon_level']
    save_file.close()

    return Game(state, game_map, objects, player, messages, dungeon_level)


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
