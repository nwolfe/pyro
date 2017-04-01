import shelve
import tcod as libtcod
from pyro.engine import Monster, GameEngine, Hero, Action, ActionResult, EventType
from pyro.objects import GameObjectFactory
from pyro.map import make_map
from pyro.game import Game
from pyro.ui import UserInterface, render_all, messagebox, menu, inventory_menu
from pyro.gameobject import GameObject
from pyro.components import AI, Fighter, Experience, Item, Inventory, Door, Graphics, Grass, Projectile, Movement
from pyro.events import EventListener
from pyro.settings import *


def move_player_or_attack(dx, dy, game):
    x = game.player.pos.x + dx
    y = game.player.pos.y + dy
    target = None
    for game_object in game.objects:
        if game_object.component(Fighter):
            if game_object.pos.equal_to(x, y):
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
                if game_object.pos.equal_to(x, y):
                    door = game_object.component(Door)
            elif game_object.component(Grass):
                if game_object.pos.equal_to(x, y):
                    if not game_object.component(Grass).is_crushed:
                        grass = game_object.component(Grass)

            if door and grass:
                break

        movement = game.player.component(Movement)
        moved = movement.move(dx, dy) if movement else False
        if moved:
            if grass:
                grass.crush()
        else:
            if door:
                door.open()
        return True, 'move'


def close_nearest_door(game):
    x = game.player.pos.x
    y = game.player.pos.y
    for game_object in game.objects:
        if game_object.component(Door):
            other_x = game_object.pos.x
            other_y = game_object.pos.y
            close_x = (other_x == x or other_x == x-1 or other_x == x+1)
            close_y = (other_y == y or other_y == y-1 or other_y == y+1)
            player_on_door = (other_x == x and other_y == y)
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

    if libtcod.KEY_UP == ui.keyboard.vk or key_char == 'k':
        return move_player_or_attack(0, -1, game)
    elif libtcod.KEY_DOWN == ui.keyboard.vk or key_char == 'j':
        return move_player_or_attack(0, 1, game)
    elif libtcod.KEY_LEFT == ui.keyboard.vk or key_char == 'h':
        return move_player_or_attack(-1, 0, game)
    elif libtcod.KEY_RIGHT == ui.keyboard.vk or key_char == 'l':
        return move_player_or_attack(1, 0, game)
    elif key_char == 'f':
        # Don't move, let the monsters come to you
        return False, None
    elif key_char == 'g':
        # Pick up an item; look for one in the player's tile
        for game_object in game.objects:
            item = game_object.component(Item)
            if item:
                if game_object.pos.equals(game.player.pos):
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
    elif libtcod.KEY_ENTER == ui.keyboard.vk:
        # Go down the stairs to the next level
        if game.stairs.pos.equals(game.player.pos):
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


def check_player_level_up(game, console):
    exp = game.player.component(Experience)

    # See if the player's XP is enough to level up
    if not exp.can_level_up():
        return

    # Ding! Level up!
    exp.level_up()
    msg = 'Your battle skills grow stronger! You reached level {}!'
    game.message(msg.format(exp.level), libtcod.yellow)

    choice = None
    while choice is None:
        fighter = game.player.component(Fighter)
        options = ['Constitution (+{0} HP, from {1})'.format(LEVEL_UP_STAT_HP, fighter.base_max_hp),
                   'Strength (+{0} attack, from {1})'.format(LEVEL_UP_STAT_POWER, fighter.base_power),
                   'Agility (+{0} defense, from {1})'.format(LEVEL_UP_STAT_DEFENSE, fighter.base_defense)]
        choice = menu(console, 'Level up! Choose a stat to raise:\n', options, LEVEL_SCREEN_WIDTH)
        if choice == 0:
            fighter.base_max_hp += LEVEL_UP_STAT_HP
            fighter.hp += LEVEL_UP_STAT_HP
        elif choice == 1:
            fighter.base_power += LEVEL_UP_STAT_POWER
        elif choice == 2:
            fighter.base_defense += LEVEL_UP_STAT_DEFENSE


class PlayerDeath(EventListener):
    def handle_event(self, player, event, context):
        if event == 'death':
            player.game.message('You died!')
            player.game.state = 'dead'
            player.component(Graphics).glyph = '%'
            player.component(Graphics).color = libtcod.dark_red


def new_game(object_factory):
    # Create the player
    exp_comp = Experience(xp=0, level=1)
    fighter_comp = Fighter(hp=PLAYER_DEFAULT_HP,
                           defense=PLAYER_DEFAULT_DEFENSE,
                           power=PLAYER_DEFAULT_POWER)
    player_inventory = Inventory(items=[])
    graphics = Graphics(glyph='@', color=libtcod.white)
    player = GameObject('Player', blocks=True,
                        components=[Movement(), exp_comp, fighter_comp, player_inventory, graphics],
                        listeners=[PlayerDeath()])

    # Generate map (not drawn to the screen yet)
    dungeon_level = 1
    (game_map, objects, stairs) = make_map(player, dungeon_level, object_factory)

    messages = []

    game = Game('playing', game_map, objects, stairs, player, messages, dungeon_level)

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
    fighter = game.player.component(Fighter)
    fighter.heal(fighter.max_hp() / 2)

    msg = 'After a rare moment of peace, you descend deeper into the heart '
    msg += 'of the dungeon...'
    game.message(msg, libtcod.red)
    game.dungeon_level += 1

    (game_map, objects, stairs) = make_map(game.player, game.dungeon_level, object_factory)

    game.map = game_map
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


class Screen:
    def __init__(self):
        pass

    def update(self):
        pass

    def render(self):
        pass


class DefaultScreen(Screen):
    def __init__(self, ui, game, factory):
        Screen.__init__(self)
        self.ui = ui
        self.game = game
        self.factory = factory
        self.fov_recompute = True

    def render(self):
        render_all(self.ui, self.game, self.fov_recompute)

    def update(self):
        self.fov_recompute, player_action = handle_keys(self.ui, self.game, self.factory)
        if player_action == 'exit':
            return True
        if self.game.state == 'playing' and player_action != 'idle':
            for game_object in self.game.objects:
                ai = game_object.component(AI)
                if ai:
                    ai.take_turn()
        return False


class WalkAction(Action):
    def __init__(self, dx, dy):
        Action.__init__(self)
        self.dx, self.dy = dx, dy

    def on_perform(self):
        # TODO Inline move_player_or_attack
        move_player_or_attack(self.dx, self.dy, self.game)
        return ActionResult.SUCCESS


class PickUpAction(Action):
    def __init__(self):
        Action.__init__(self)

    # TODO Do this properly; use self.actor not game.player
    def on_perform(self):
        # Pick up first item in the player's tile
        for go in self.game.objects:
            item = go.component(Item)
            if item:
                if go.pos.equals(self.game.player.pos):
                    item.pick_up(self.game.player)
        return ActionResult.SUCCESS


class EngineScreen(Screen):
    def __init__(self, ui, game, factory):
        Screen.__init__(self)
        self.game = game
        self.ui = ui
        self.factory = factory
        self.fov_recompute = True
        # TODO This logic can't be here
        self.hero = Hero(game.player, game)
        actors = [self.hero]
        for go in self.game.objects:
            if go.component(AI):
                actors.append(Monster(go, self.game))
        self.engine = GameEngine(actors)

    def handle_input(self, keyboard):
        action = None
        key_char = chr(keyboard.c)
        # TODO Implement all keybindings
        if libtcod.KEY_ESCAPE == keyboard.vk:
            return 'exit'
        elif libtcod.KEY_UP == keyboard.vk:
            action = WalkAction(0, -1)
        elif libtcod.KEY_DOWN == keyboard.vk:
            action = WalkAction(0, 1)
        elif libtcod.KEY_LEFT == keyboard.vk:
            action = WalkAction(-1, 0)
        elif libtcod.KEY_RIGHT == keyboard.vk:
            action = WalkAction(1, 0)
        elif 'g' == key_char:
            action = PickUpAction()
        if action:
            self.hero.next_action = action
        return None

    def render(self):
        # TODO render effects
        render_all(self.ui, self.game, self.fov_recompute)

    def update(self):
        if 'exit' == self.handle_input(self.ui.keyboard):
            return True
        result = self.engine.update()
        # TODO Create Effects for Events and update them
        # for event in result.events:
        #     if EventType.HIT == event.type:
        #         pass
        #     elif EventType.BOLT == event.type:
        #         pass

        return False


def play_game(game, ui, object_factory):
    for game_object in game.objects:
        game_object.game = game

    libtcod.console_clear(ui.console)
    # screen = DefaultScreen(ui, game, object_factory)
    screen = EngineScreen(ui, game, object_factory)
    while not libtcod.console_is_window_closed():
        screen.render()

        while update_projectiles(game):
            render_all(ui, game, False)

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

    return Game(state, game_map, objects, stairs, player, messages, dungeon_level)


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
