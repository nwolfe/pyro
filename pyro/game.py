import libtcodpy as libtcod
from textwrap import wrap
from pyro.components import Fighter
from pyro.ui import render_all
from pyro.utilities import is_blocked
from pyro.settings import MSG_WIDTH, MSG_HEIGHT


class Game:
    def __init__(self,
                 state=None,
                 game_map=None,
                 fov_map=None,
                 objects=None,
                 stairs=None,
                 player=None,
                 messages=None,
                 dungeon_level=1):
        self.state = state
        self.game_map = game_map
        self.fov_map = fov_map
        self.stairs = stairs
        self.objects = objects
        self.player = player
        self.messages = messages
        self.dungeon_level = dungeon_level

        if self.messages is None:
            self.messages = []

    def add_object(self, game_object):
        self.objects.append(game_object)

    def remove_object(self, game_object):
        if game_object in self.objects:
            self.objects.remove(game_object)

    def is_blocked(self, x, y):
        return is_blocked(self.game_map, self.objects, x, y)

    def message(self, text, color=libtcod.white):
        # Split the message if necessary, among multiple lines
        new_msg_lines = wrap(text, MSG_WIDTH)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room
            if len(self.messages) == MSG_HEIGHT:
                del self.messages[0]

            # Add the new line as a tuple, with the text and color
            self.messages.append((line, color))

    def target_tile(self, ui, max_range=None):
        # Return the position of a tile left-clicked in player's FOV
        # (optionally in a range), or (None, None) if right-clicked.
        while True:
            # Render the screen. This erases the inventory and shows the names of
            # objects under the mouse.
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE,
                                        ui.keyboard, ui.mouse)
            render_all(ui, self, False)

            (x, y) = (ui.mouse.cx, ui.mouse.cy)

            if (ui.mouse.lbutton_pressed and libtcod.map_is_in_fov(self.fov_map, x, y)
                    and (max_range is None or self.player.distance(x, y) <= max_range)):
                return x, y

            if ui.mouse.rbutton_pressed or ui.keyboard.vk == libtcod.KEY_ESCAPE:
                return None, None

    def target_monster(self, ui, max_range=None):
        # Returns a clicked monster inside FOV up to a range, or None if
        # right-clicked
        while True:
            (x, y) = self.target_tile(ui, max_range)
            if x is None:
                return None

            # Return the first clicked monster, otherwise continue looking
            for game_object in self.objects:
                if game_object != self.player:
                    if game_object.component(Fighter):
                        if game_object.x == x and game_object.y == y:
                            return game_object

    def closest_monster(self, max_range):
        # Find closest enemy, up to a maximum range, and in the player's FOV
        closest_enemy = None
        closest_dist = max_range + 1

        for game_object in self.objects:
            if game_object != self.player and game_object.component(Fighter):
                if libtcod.map_is_in_fov(self.fov_map, game_object.x, game_object.y):
                    # Calculate distance between this object and the player
                    dist = self.player.distance_to(game_object)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_enemy = game_object

        return closest_enemy
