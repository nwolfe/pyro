import tcod as libtcod
from itertools import chain
from pyro.ui import Screen
from pyro.components import AI, Experience, Graphics, Physics, Inventory, Equipment, Item
from pyro.direction import Direction
from pyro.engine import Monster, GameEngine, EventType
from pyro.engine.actions import PickUpAction, WalkAction, CloseDoorAction, UseAction, DropAction
from pyro.map import make_map
from pyro.ui import HitEffect
from pyro.settings import *


class EngineScreen(Screen):
    def __init__(self, ui, game, factory):
        Screen.__init__(self)
        self.game = game
        self.ui = ui
        self.factory = factory
        self.effects = []
        self.hero = None
        self.engine = None
        self.initialize_engine()

    def initialize_engine(self):
        # TODO This logic can't be here
        self.hero = self.game.player
        actors = [self.hero]
        for go in self.game.objects:
            if go != self.hero:
                monster = Monster(self.game, go)
                go.actor = monster
                actors.append(monster)
        self.engine = GameEngine(actors)
        self.game.actors = actors

    def handle_input(self):
        action = None
        key_char = chr(self.ui.keyboard.c)
        if libtcod.KEY_ESCAPE == self.ui.keyboard.vk:
            return True
        elif libtcod.KEY_UP == self.ui.keyboard.vk:
            action = WalkAction(Direction.NORTH)
        elif libtcod.KEY_DOWN == self.ui.keyboard.vk:
            action = WalkAction(Direction.SOUTH)
        elif libtcod.KEY_LEFT == self.ui.keyboard.vk:
            action = WalkAction(Direction.WEST)
        elif libtcod.KEY_RIGHT == self.ui.keyboard.vk:
            action = WalkAction(Direction.EAST)
        elif libtcod.KEY_ENTER == self.ui.keyboard.vk:
            pos = self.game.player.pos
            if self.game.map.tile(pos).type.is_exit:
                self.next_dungeon_level()
                libtcod.console_clear(self.ui.console)
        elif 'c' == key_char:
            show_character_info(self.ui.console, self.game)
        elif 'd' == key_char:
            # Show the inventory; if an item is selected, drop it
            msg = 'Select an item to drop it, or any other key to cancel.\n'
            inventory = self.game.player.component(Inventory).items
            selected_item = inventory_menu(self.ui.console, inventory, msg)
            if selected_item:
                action = DropAction(selected_item)
        elif 'f' == key_char:
            # Wait; do nothing and let the world continue
            action = WalkAction(Direction.NONE)
        elif 'g' == key_char:
            action = PickUpAction()
        elif 'i' == key_char:
            # Show the inventory; if an item is selected, use it
            msg = 'Select an item to use it, or any other key to cancel.\n'
            inventory = self.game.player.component(Inventory).items
            selected_item = inventory_menu(self.ui.console, inventory, msg)
            if selected_item:
                action = UseAction(selected_item, self.ui)
        elif 'r' == key_char:
            action = CloseDoorAction(self.game.player.pos)
        if action:
            self.hero.next_action = action
        return False

    def update(self):
        if self.game.state == 'dead':
            return

        result = self.engine.update(self.game)

        if not self.game.player.is_alive():
            self.game.state = 'dead'
            self.game.log.message('You died!')
            self.game.player.component(Graphics).glyph = '%'
            self.game.player.component(Graphics).color = libtcod.dark_red
            return

        for event in result.events:
                if EventType.HIT == event.type:
                    self.effects.append(HitEffect(event.actor))
                elif EventType.DEATH == event.type:
                    if event.actor != self.game.player:
                        monster_death(event.actor, event.other, self.game)

        self.effects = filter(lambda e: e.update(self.game), self.effects)

    def render(self):
        # TODO is there more to this?
        # Draw tiles
        for y in range(self.game.map.height):
            for x in range(self.game.map.width):
                tile = self.game.map.tiles[x][y]
                visible = self.game.map.is_in_fov(x, y)
                if not visible:
                    if tile.explored:
                        glyph = tile.type.appearance.unlit
                        libtcod.console_set_char_background(self.ui.console, x, y, glyph.bg_color, libtcod.BKGND_SET)
                        if tile.type.always_visible and glyph.char:
                            libtcod.console_set_default_foreground(self.ui.console, glyph.fg_color)
                            libtcod.console_put_char(self.ui.console, x, y, glyph.char, libtcod.BKGND_NONE)
                else:
                    tile.explored = True
                    glyph = tile.type.appearance.lit
                    libtcod.console_set_char_background(self.ui.console, x, y, glyph.bg_color, libtcod.BKGND_SET)
                    if glyph.char:
                        libtcod.console_set_default_foreground(self.ui.console, glyph.fg_color)
                        libtcod.console_put_char(self.ui.console, x, y, glyph.char, libtcod.BKGND_NONE)

        # Draw game items
        render_ordered = sorted(self.game.items, key=lambda i: i.component(Graphics).render_order)
        for game_item in render_ordered:
            game_item.component(Graphics).draw(self.ui.console)

        # Draw game objects
        render_ordered = sorted(self.game.objects, key=lambda o: o.component(Graphics).render_order)
        for game_object in render_ordered:
            game_object.component(Graphics).draw(self.ui.console)

        # Draw effects
        for effect in self.effects:
            effect.render(self.game, self.ui)

        # Blit the contents of the game (non-GUI) console to the root console
        libtcod.console_blit(self.ui.console, 0, 0, self.game.map.width, self.game.map.height, 0, 0, 0)

        # Prepare to render the GUI panel
        libtcod.console_set_default_background(self.ui.panel, libtcod.black)
        libtcod.console_clear(self.ui.panel)

        # Print game messages, one line at a time
        y = 1
        for (line, color) in self.game.log.messages:
            libtcod.console_set_default_foreground(self.ui.panel, color)
            libtcod.console_print_ex(self.ui.panel, MSG_X, y, libtcod.BKGND_NONE,
                                     libtcod.LEFT, line)
            y += 1

        # Show player's stats
        render_ui_bar(self.ui.panel, 1, 1, BAR_WIDTH, 'HP', self.game.player.hp,
                      self.game.player.max_hp, libtcod.light_red, libtcod.darker_red)
        experience = self.game.player.component(Experience)
        render_ui_bar(self.ui.panel, 1, 2, BAR_WIDTH, 'EXP', experience.xp, experience.required_for_level_up(),
                      libtcod.green, libtcod.darkest_green)

        # Show the dungeon level
        libtcod.console_print_ex(self.ui.panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                                 'Dungeon Level {}'.format(self.game.dungeon_level))

        # Display names of objects under the mouse
        names = get_names_under_mouse(self.ui.mouse, self.game)
        libtcod.console_set_default_foreground(self.ui.panel, libtcod.light_gray)
        libtcod.console_print_ex(self.ui.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                                 names)

        # Blit the contents of the GUI panel to the root console
        libtcod.console_blit(self.ui.panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0,
                             PANEL_Y)

        libtcod.console_flush()
        for y in range(self.game.map.height):
            for x in range(self.game.map.width):
                libtcod.console_put_char(self.ui.console, x, y, ' ', libtcod.BKGND_NONE)

    def next_dungeon_level(self):
        # Advance to the next level
        # Heal the player by 50%
        self.game.log.message('You take a moment to rest, and recover your strength.',
                              libtcod.light_violet)
        self.game.player.heal(self.game.player.max_hp / 2)

        msg = 'After a rare moment of peace, you descend deeper into the heart '
        msg += 'of the dungeon...'
        self.game.log.message(msg, libtcod.red)
        self.game.dungeon_level += 1

        make_map(self.game, self.factory)

        self.initialize_engine()


def monster_death(monster, attacker, game):
    monster = monster.game_object
    attacker = attacker.game_object
    # Transform it into a nasty corpse!
    # It doesn't block, can't be attacked, and doesn't move
    exp = monster.component(Experience)
    if attacker == game.player:
        game.log.message('The {0} is dead! You gain {1} experience points.'.
                         format(monster.name, exp.xp), libtcod.orange)
    else:
        game.log.message('The {0} is dead!'.format(monster.name), libtcod.orange)
    attacker.component(Experience).xp += exp.xp
    monster.name = 'Remains of {0}'.format(monster.name)
    monster.component(Graphics).glyph = '%'
    monster.component(Graphics).color = libtcod.dark_red
    monster.component(Graphics).render_order = RENDER_ORDER_CORPSE
    monster.component(Physics).blocks = False
    monster.remove_component(AI)


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


def get_names_under_mouse(mouse, game):
    # Return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    # Create a list with the names of all objects at the mouse's coordinates
    # and in FOV
    names = [obj.name for obj in chain(game.objects, game.items)
             if obj.pos.equal_to(x, y) and game.map.is_in_fov(obj.pos.x, obj.pos.y)]
    return ', '.join(names)


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
    menu(console, msg, [], CHARACTER_SCREEN_WIDTH)
