import libtcodpy as libtcod
from itertools import chain
from pyro.ui import Screen
from pyro.direction import Direction
from pyro.engine.actions import PickUpAction, WalkAction, CloseDoorAction, UseAction, DropAction
from pyro.map import make_map
from pyro.ui.effects import add_effects
from pyro.ui.menu_screen import MenuScreen
from pyro.ui.targetscreen import TargetScreen
from pyro.ui.pausescreen import PauseScreen
from pyro.settings import *
from pyro.target import Target, TargetRequire
from pyro.utilities import closest_monster
from pyro.engine.log import LogType
from pyro.engine.element import Elements
import pyro.ui.inputs as inputs


_MESSAGE_COLORS = {
    LogType.MESSAGE: libtcod.white,
    LogType.ERROR: libtcod.red,
    LogType.NOTIFY: libtcod.cyan,
    LogType.GAIN: libtcod.light_green,
    LogType.ELEMENTAL: None,
    Elements.FIRE: libtcod.orange,
    Elements.LIGHTNING: libtcod.light_blue
}


class GameScreen(Screen):
    def __init__(self, game):
        Screen.__init__(self)
        self.game = game
        self.effects = []

    def handle_input(self, input_):
        action = None
        if inputs.EXIT == input_:
            self.ui.push(PauseScreen(), tag='game.pause')
        elif inputs.NORTH == input_:
            action = WalkAction(Direction.NORTH)
        elif inputs.SOUTH == input_:
            action = WalkAction(Direction.SOUTH)
        elif inputs.WEST == input_:
            action = WalkAction(Direction.WEST)
        elif inputs.EAST == input_:
            action = WalkAction(Direction.EAST)
        elif inputs.ENTER == input_:
            pos = self.game.player.pos
            if self.game.stage.map.tile(pos).type.is_exit:
                self.next_dungeon_level()
        elif inputs.HERO_INFO == input_:
            info = character_info(self.game.player)
            self.ui.push(MenuScreen(info, [], CHARACTER_SCREEN_WIDTH))
        elif inputs.DROP == input_:
            # Show the inventory; if an item is selected, drop it
            msg = 'Select an item to drop it, or any other key to cancel.\n'
            inventory = self.game.player.inventory
            drop_item_screen = MenuScreen(msg, inventory, INVENTORY_WIDTH,
                                          empty_text='Inventory is empty')
            self.ui.push(drop_item_screen, tag='item.drop')
        elif inputs.REST == input_:
            # Wait; do nothing and let the world continue
            action = WalkAction(Direction.NONE)
        elif inputs.PICKUP == input_:
            items_at_player = filter(lambda i: i.pos == self.game.player.pos,
                                     self.game.stage.items)
            # TODO Handle multiple items better; selection menu?
            if len(items_at_player) > 0:
                action = PickUpAction(items_at_player[0])
            else:
                self.game.log.error('There is nothing here.')
                self.dirty()
        elif inputs.INVENTORY == input_:
            # Show the inventory; if an item is selected, use it
            msg = 'Select an item to use it, or any other key to cancel.\n'
            inventory = self.game.player.inventory
            use_item_screen = MenuScreen(msg, inventory, INVENTORY_WIDTH,
                                         empty_text='Inventory is empty')
            self.ui.push(use_item_screen, tag='item.use')
        elif inputs.CLOSE_DOOR == input_:
            action = CloseDoorAction(self.game.player.pos)
        if action:
            self.game.player.next_action = action
        return True

    def activate(self, result=None, tag=None, data=None):
        if result is None:
            return

        if 'item.use' == tag:
            item = result.choice
            require = item.requires_target()
            if TargetRequire.TYPE_NONE == require.type:
                self.game.player.next_action = UseAction(item)
            elif TargetRequire.TYPE_SELF == require.type:
                self.game.player.next_action = UseAction(item, Target(self.game.player))
            elif TargetRequire.TYPE_NEAREST == require.type:
                nearest = closest_monster(self.game, require.range)
                if nearest:
                    self.game.player.next_action = UseAction(item, Target(nearest))
                else:
                    self.game.log.error(require.not_found_message)
                    self.dirty()
            elif TargetRequire.TYPE_SELECT == require.type:
                self.ui.push(TargetScreen(self, require.range),
                             tag='item.select-target', data=item)
        elif 'item.select-target' == tag:
            item, target = data, result
            self.game.player.next_action = UseAction(item, target)
        elif 'item.drop' == tag:
            self.game.player.next_action = DropAction(result.choice)
        elif 'level-up.stat' == tag:
            if result.index == 0:
                self.game.player.base_max_hp += LEVEL_UP_STAT_HP
                self.game.player.hp += LEVEL_UP_STAT_HP
            elif result.index == 1:
                self.game.player.base_power += LEVEL_UP_STAT_POWER
            elif result.index == 2:
                self.game.player.base_defense += LEVEL_UP_STAT_DEFENSE
        elif 'game.pause' == tag:
                # New Game or Quit was selected; exit and pass along choice
                self.ui.pop(result)

    def update(self):
        if self.game.player.is_alive():
            if self.game.player.can_level_up():
                self._level_up_player()

            if len(self.effects) > 0:
                self.dirty()

            result = self.game.update()

            for event in result.events:
                add_effects(self.effects, event)

            if result.needs_refresh():
                self.dirty()

        self.effects = filter(lambda e: e.update(self.game), self.effects)

    def handle_mouse_move(self, mouse):
        self.dirty()

    def _level_up_player(self):
        # Only push one level-up screen at a time
        if self.ui.top_screen().tag == 'level-up.stat':
            return

        # Ding! Level up!
        self.game.player.level_up()
        msg = 'Your battle skills grow stronger! You reached level {}!'
        self.game.log.gain(msg.format(self.game.player.level))
        self.dirty()
        options = ['Constitution (+{0} HP, from {1})'.format(LEVEL_UP_STAT_HP, self.game.player.base_max_hp),
                   'Strength (+{0} attack, from {1})'.format(LEVEL_UP_STAT_POWER, self.game.player.base_power),
                   'Agility (+{0} defense, from {1})'.format(LEVEL_UP_STAT_DEFENSE, self.game.player.base_defense)]
        level_up_screen = MenuScreen('Level up! Choose a stat to raise:\n', options, LEVEL_SCREEN_WIDTH,
                                     require_selection=True)
        self.ui.push(level_up_screen, tag='level-up.stat')

    def render(self):
        # TODO is there more to this?
        # Draw tiles
        for y in range(self.game.stage.map.height):
            for x in range(self.game.stage.map.width):
                tile = self.game.stage.map.tiles[x][y]
                visible = self.game.stage.map.is_xy_in_fov(x, y)
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
        for item in self.game.stage.items:
            if self.game.stage.map.is_in_fov(item.pos):
                libtcod.console_set_default_foreground(self.ui.console, item.glyph.fg_color)
                libtcod.console_put_char(self.ui.console, item.pos.x, item.pos.y,
                                         item.glyph.char, libtcod.BKGND_NONE)

        # Draw corpses
        for corpse in self.game.stage.corpses:
            if self.game.stage.map.is_in_fov(corpse.pos):
                glyph = corpse.type.glyph
                libtcod.console_set_default_foreground(self.ui.console, glyph.fg_color)
                libtcod.console_put_char(self.ui.console, corpse.pos.x, corpse.pos.y,
                                         glyph.char, libtcod.BKGND_NONE)

        # Draw game actors
        for actor in self.game.stage.actors:
            if self.game.stage.map.is_in_fov(actor.pos):
                libtcod.console_set_default_foreground(self.ui.console, actor.glyph.fg_color)
                libtcod.console_put_char(self.ui.console, actor.pos.x, actor.pos.y,
                                         actor.glyph.char, libtcod.BKGND_NONE)

        # Draw effects
        for effect in self.effects:
            effect.render(self.game, self.ui)

        # Blit the contents of the game (non-GUI) console to the root console
        libtcod.console_blit(self.ui.console, 0, 0, self.game.stage.map.width, self.game.stage.map.height, 0, 0, 0)

        # Print game messages, one line at a time
        y = 1
        for message in self.game.log.messages:
            color = _MESSAGE_COLORS[message.type]
            if message.type == LogType.ELEMENTAL:
                color = _MESSAGE_COLORS[message.element]
            libtcod.console_set_default_foreground(self.ui.panel, color)
            libtcod.console_print_ex(self.ui.panel, MSG_X, y, libtcod.BKGND_NONE,
                                     libtcod.LEFT, message.text)
            if message.count > 1:
                count = '(%d)' % message.count
                libtcod.console_set_default_foreground(self.ui.panel, libtcod.gray)
                libtcod.console_print_ex(self.ui.panel, MSG_X + len(message.text), y,
                                         libtcod.BKGND_NONE, libtcod.LEFT, count)
            y += 1

        # Show player's stats
        render_ui_bar(self.ui.panel, 1, 1, BAR_WIDTH, 'HP', self.game.player.hp,
                      self.game.player.max_hp, libtcod.light_red, libtcod.darker_red)
        render_ui_bar(self.ui.panel, 1, 2, BAR_WIDTH, 'EXP', self.game.player.xp,
                      self.game.player.required_for_level_up(), libtcod.green, libtcod.darkest_green)

        # Show the dungeon level
        libtcod.console_print_ex(self.ui.panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                                 'Dungeon Level {}'.format(self.game.dungeon_level))

        # Display names of objects under the mouse
        names = get_names_under_mouse(self.ui.mouse, self.game)
        libtcod.console_set_default_foreground(self.ui.panel, libtcod.light_gray)
        libtcod.console_print_ex(self.ui.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                                 names)

        # Reset the background color for next time
        libtcod.console_set_default_background(self.ui.panel, libtcod.black)

        # Blit the contents of the GUI panel to the root console
        libtcod.console_blit(self.ui.panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

    def next_dungeon_level(self):
        # TODO Push all this down into a Game#next_level() method?
        # Advance to the next level
        # Heal the player by 50%
        self.game.log.message('{1} take[s] a moment to rest, and recover strength.', self.game.player)
        self.game.player.heal(self.game.player.max_hp / 2)

        msg = 'After a rare moment of peace, {1} descend deeper into the heart of the dungeon...'
        self.game.log.message(msg, self.game.player)
        self.game.dungeon_level += 1

        make_map(self.game)
        self.dirty()


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


def get_names_under_mouse(mouse, game):
    # Return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    # Create a list with the names of all objects at the mouse's coordinates
    # and in FOV
    names = [obj.name for obj in chain(game.stage.actors, game.stage.items, game.stage.corpses)
             if obj.pos.equals(x, y) and game.stage.map.is_in_fov(obj.pos)]
    return ', '.join(names)


def character_info(player):
    msg = """Character Information

Level: {0}
Experience: {1}
Next Level: {2}

Current HP: {3}
Maximum HP: {4}
Attack: {5}
Defense: {6}
"""
    return msg.format(player.level,
                      player.xp,
                      player.required_for_level_up(),
                      player.hp,
                      player.max_hp,
                      player.power,
                      player.defense)
