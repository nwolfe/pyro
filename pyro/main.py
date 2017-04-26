import tcod as libtcod
from pyro.components import Experience, Item, Graphics
from pyro.map import make_map
from pyro.objects import GameObjectFactory, make_player
from pyro.settings import SCREEN_HEIGHT, SCREEN_WIDTH, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGORITHM
from pyro.settings import COLOR_DARK_WALL, COLOR_DARK_GROUND, COLOR_LIGHT_WALL, COLOR_LIGHT_GRASS, COLOR_LIGHT_GROUND
from pyro.settings import MSG_X, BAR_WIDTH, PANEL_HEIGHT, PANEL_Y, MAP_WIDTH, MAP_HEIGHT
from pyro.settings import LEVEL_UP_STAT_HP, LEVEL_UP_STAT_POWER, LEVEL_UP_STAT_DEFENSE, LEVEL_SCREEN_WIDTH, LIMIT_FPS
from pyro.ui import EngineScreen
from pyro.engine.log import Log


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

    render_ordered = sorted(game.items, key=lambda o: o.component(Graphics).render_order)
    for game_item in render_ordered:
        game_item.component(Graphics).draw(ui.console)

    render_ordered = sorted(game.actors, key=lambda o: o.component(Graphics).render_order)
    for game_object in render_ordered:
        game_object.component(Graphics).draw(ui.console)

    # Blit the contents of the game (non-GUI) console to the root console
    libtcod.console_blit(ui.console, 0, 0, game.map.width, game.map.height, 0, 0, 0)

    # Prepare to render the GUI panel
    libtcod.console_set_default_background(ui.panel, libtcod.black)
    libtcod.console_clear(ui.panel)

    # Print game messages, one line at a time
    y = 1
    for (line, color) in game.log.messages:
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
    names = get_names_under_mouse(ui.mouse, game.actors, game.map)
    libtcod.console_set_default_foreground(ui.panel, libtcod.light_gray)
    libtcod.console_print_ex(ui.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             names)

    # Blit the contents of the GUI panel to the root console
    libtcod.console_blit(ui.panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0,
                         PANEL_Y)

    libtcod.console_flush()
    for game_object in game.actors:
        game_object.component(Graphics).clear(ui.console)
    for game_item in game.items:
        game_item.component(Graphics).clear(ui.console)


###############################################################################
# Game Logic                                                                  #
###############################################################################


def check_player_level_up(game, console):
    player = game.player.game_object
    exp = player.component(Experience)

    # See if the player's XP is enough to level up
    if not exp.can_level_up():
        return

    # Ding! Level up!
    exp.level_up()
    msg = 'Your battle skills grow stronger! You reached level {}!'
    game.log.message(msg.format(exp.level), libtcod.yellow)

    choice = None
    while choice is None:
        options = ['Constitution (+{0} HP, from {1})'.format(LEVEL_UP_STAT_HP, player.__base_max_hp__),
                   'Strength (+{0} attack, from {1})'.format(LEVEL_UP_STAT_POWER, player.__base_power__),
                   'Agility (+{0} defense, from {1})'.format(LEVEL_UP_STAT_DEFENSE, player.__base_defense__)]
        choice = menu(console, 'Level up! Choose a stat to raise:\n', options, LEVEL_SCREEN_WIDTH)
        if choice == 0:
            player.__base_max_hp__ += LEVEL_UP_STAT_HP
            player.__hp__ += LEVEL_UP_STAT_HP
        elif choice == 1:
            player.__base_power__ += LEVEL_UP_STAT_POWER
        elif choice == 2:
            player.__base_defense__ += LEVEL_UP_STAT_DEFENSE


class Game:
    def __init__(self, state=None, map=None, objects=None, player=None, log=None, dungeon_level=None):
        self.state = state
        self.map = map
        self.actors = objects
        self.items = None
        self.player = player
        self.log = log
        self.dungeon_level = dungeon_level


def new_game(object_factory):
    game = Game(state='playing', log=Log(), dungeon_level=1)
    player = make_player(game)
    object_factory.game = game
    make_map(game, object_factory)

    # Initial equipment: a dagger and scroll of lightning bolt
    dagger = object_factory.new_item('Dagger')
    dagger.component(Item).pick_up(player)

    spell = object_factory.new_item('Scroll Of Lightning Bolt')
    spell.component(Item).pick_up(player)

    spell = object_factory.new_item('Scroll Of Fireball')
    spell.component(Item).pick_up(player)

    spell = object_factory.new_item('Scroll Of Confusion')
    spell.component(Item).pick_up(player)

    game.log.messages = []
    m = 'Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings!'
    game.log.message(m, libtcod.red)

    return game


def play_game(game, ui, object_factory):
    libtcod.console_clear(ui.console)
    screen = EngineScreen(ui, game, object_factory)
    while not libtcod.console_is_window_closed():
        screen.render()

        check_player_level_up(game, ui.console)

        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS |
                                    libtcod.EVENT_MOUSE, ui.keyboard, ui.mouse)

        if screen.handle_input():
            break
        screen.update()


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
        options = ['Play a new game', 'Quit']
        choice = menu(ui.console, '', options, 24)

        if choice == 0:
            # New game
            game = new_game(object_factory)
            play_game(game, ui, object_factory)
        elif choice == 1:
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
