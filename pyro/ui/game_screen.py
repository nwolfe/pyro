import tcod as libtcod
from pyro.ui import Screen
from pyro.components import AI, Experience, Fighter, Graphics
from pyro.direction import Direction
from pyro.engine import Hero, Monster, GameEngine, EventType
from pyro.engine.actions import PickUpAction, WalkAction
from pyro.ui import HitEffect
from pyro.settings import *


class EngineScreen(Screen):
    def __init__(self, ui, game, factory):
        Screen.__init__(self)
        self.game = game
        self.ui = ui
        self.factory = factory
        self.fov_recompute = True
        self.effects = []
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
            action = WalkAction(Direction.NORTH)
        elif libtcod.KEY_DOWN == keyboard.vk:
            action = WalkAction(Direction.SOUTH)
        elif libtcod.KEY_LEFT == keyboard.vk:
            action = WalkAction(Direction.WEST)
        elif libtcod.KEY_RIGHT == keyboard.vk:
            action = WalkAction(Direction.EAST)
        elif 'g' == key_char:
            action = PickUpAction()
        if action:
            self.hero.next_action = action
        return None

    def render(self):
        render_all(self.ui, self.game, self.fov_recompute)
        # TODO render effects
        # for effect in self.effects:
        #     effect.render(self.game, self.ui)
        # libtcod.console_blit(self.ui.console, 0, 0, self.game.map.width, self.game.map.height, 0, 0, 0)
        # libtcod.console_flush()

    def update(self):
        if 'exit' == self.handle_input(self.ui.keyboard):
            return True
        result = self.engine.update()
        # TODO Create Effects for Events and update them
        for event in result.events:
            if EventType.HIT == event.type:
                self.effects.append(HitEffect(event.actor))

        self.effects = filter(lambda e: e.update(self.game), self.effects)

        return False


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
    fighter = game.player.component(Fighter)
    render_ui_bar(ui.panel, 1, 1, BAR_WIDTH, 'HP', fighter.hp,
                  fighter.max_hp(), libtcod.light_red, libtcod.darker_red)
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
