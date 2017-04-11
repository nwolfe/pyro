import tcod as libtcod
from pyro.ui import Screen
from pyro.components import AI, Experience, Fighter, Graphics, Physics
from pyro.direction import Direction
from pyro.engine import Hero, Monster, GameEngine, EventType
from pyro.engine.actions import PickUpAction, WalkAction, CloseDoorAction
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
        self.hero = Hero(self.game, self.game.player)
        actors = [self.hero]
        for go in self.game.objects:
            if go.component(AI):
                actors.append(Monster(self.game, go))
        self.engine = GameEngine(actors)
        self.game.actors = actors

    def handle_input(self, keyboard):
        action = None
        key_char = chr(keyboard.c)
        # TODO Implement all keybindings
        if libtcod.KEY_ESCAPE == keyboard.vk:
            return 'exit'
        elif libtcod.KEY_UP == keyboard.vk:
            action = WalkAction(Direction.NORTH)
        elif libtcod.KEY_DOWN == keyboard.vk:
            action = WalkAction(Direction.SOUTH)
        elif libtcod.KEY_LEFT == keyboard.vk:
            action = WalkAction(Direction.WEST)
        elif libtcod.KEY_RIGHT == keyboard.vk:
            action = WalkAction(Direction.EAST)
        elif libtcod.KEY_ENTER == keyboard.vk:
            pos = self.game.player.pos
            if self.game.map.tiles[pos.x][pos.y].type.is_exit:
                self.next_dungeon_level()
                libtcod.console_clear(self.ui.console)
        elif 'g' == key_char:
            action = PickUpAction()
        elif 'r' == key_char:
            action = CloseDoorAction()
        if action:
            self.hero.next_action = action
        return None

    def update(self):
        if 'exit' == self.handle_input(self.ui.keyboard):
            return True

        if self.game.state == 'dead':
            return False

        result = self.engine.update(self.game)

        for event in result.events:
            if EventType.HIT == event.type:
                self.effects.append(HitEffect(event.actor))
            elif EventType.DEATH == event.type:
                if event.actor == self.game.player:
                    player_death(self.game)
                else:
                    monster_death(event.actor, event.other, self.game)

        self.effects = filter(lambda e: e.update(self.game), self.effects)

        return False

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
        for (line, color) in self.game.messages:
            libtcod.console_set_default_foreground(self.ui.panel, color)
            libtcod.console_print_ex(self.ui.panel, MSG_X, y, libtcod.BKGND_NONE,
                                     libtcod.LEFT, line)
            y += 1

        # Show player's stats
        fighter = self.game.player.component(Fighter)
        render_ui_bar(self.ui.panel, 1, 1, BAR_WIDTH, 'HP', fighter.hp,
                      fighter.max_hp(), libtcod.light_red, libtcod.darker_red)
        experience = self.game.player.component(Experience)
        render_ui_bar(self.ui.panel, 1, 2, BAR_WIDTH, 'EXP', experience.xp, experience.required_for_level_up(),
                      libtcod.green, libtcod.darkest_green)

        # Show the dungeon level
        libtcod.console_print_ex(self.ui.panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                                 'Dungeon Level {}'.format(self.game.dungeon_level))

        # Display names of objects under the mouse
        names = get_names_under_mouse(self.ui.mouse, self.game.objects, self.game.map)
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
        self.game.message('You take a moment to rest, and recover your strength.',
                          libtcod.light_violet)
        fighter = self.game.player.component(Fighter)
        fighter.heal(fighter.max_hp() / 2)

        msg = 'After a rare moment of peace, you descend deeper into the heart '
        msg += 'of the dungeon...'
        self.game.message(msg, libtcod.red)
        self.game.dungeon_level += 1

        (game_map, objects) = make_map(self.game.player, self.game.dungeon_level, self.factory)

        self.game.map = game_map
        self.game.objects = objects

        for game_object in self.game.objects:
            game_object.game = self.game

        self.initialize_engine()


def player_death(game):
    game.message('You died!')
    game.state = 'dead'
    game.player.component(Graphics).glyph = '%'
    game.player.component(Graphics).color = libtcod.dark_red


def monster_death(monster, attacker, game):
    # Transform it into a nasty corpse!
    # It doesn't block, can't be attacked, and doesn't move
    exp = monster.component(Experience)
    if attacker == game.player:
        game.message('The {0} is dead! You gain {1} experience points.'.
                     format(monster.name, exp.xp), libtcod.orange)
    else:
        game.message('The {0} is dead!'.format(monster.name), libtcod.orange)
    attacker.component(Experience).xp += exp.xp
    monster.name = 'Remains of {0}'.format(monster.name)
    monster.component(Graphics).glyph = '%'
    monster.component(Graphics).color = libtcod.dark_red
    monster.component(Graphics).render_order = RENDER_ORDER_CORPSE
    monster.component(Physics).blocks = False
    monster.remove_component(Fighter)
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


def get_names_under_mouse(mouse, objects, game_map):
    # Return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    # Create a list with the names of all objects at the mouse's coordinates
    # and in FOV
    names = [obj.name for obj in objects
             if obj.pos.equal_to(x, y) and game_map.is_in_fov(obj.pos.x, obj.pos.y)]
    return ', '.join(names).capitalize()
