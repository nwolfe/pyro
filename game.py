import libtcodpy as libtcod
import ui as libui
import textwrap
from settings import *

def message(messages, new_msg, color=libtcod.white):
    # Split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        # If the buffer is full, remove the first line to make room
        if len(messages) == MSG_HEIGHT:
            del messages[0]

        # Add the new line as a tuple, with the text and color
        messages.append((line, color))


class Game:
    def __init__(self,
                 state=None,
                 console=None,
                 panel=None,
                 mouse=None,
                 key=None,
                 map=None,
                 fov_map=None,
                 objects=None,
                 stairs=None,
                 player=None,
                 inventory=None,
                 messages=None,
                 dungeon_level=1):
        self.state = state
        self.console = console
        self.panel = panel
        self.mouse = mouse
        self.key = key
        self.map = map
        self.fov_map = fov_map
        self.stairs = stairs
        self.objects = objects
        self.player = player
        self.inventory = inventory
        self.messages = messages
        self.dungeon_level = dungeon_level

    def message(self, text, color=libtcod.white):
        message(self.messages, text, color)

    def target_tile(self, max_range=None):
        # Return the position of a tile left-clicked in player's FOV
        # (optionally in a range), or (None, None) if right-clicked.
        while True:
            # Render the screen. This erases the inventory and shows the names of
            # objects under the mouse.
            libtcod.console_flush()
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS |
                                        libtcod.EVENT_MOUSE,
                                        self.key, self.mouse)
            libui.render_all(self, False)

            (x, y) = (self.mouse.cx, self.mouse.cy)

            if (self.mouse.lbutton_pressed and
                libtcod.map_is_in_fov(self.fov_map, x, y) and
                (max_range is None or self.player.distance(x, y) <= max_range)):
                return (x, y)

            if self.mouse.rbutton_pressed or self.key.vk == libtcod.KEY_ESCAPE:
                return (None, None)

    def target_monster(self, max_range=None):
        # Returns a clicked monster inside FOV up to a range, or None if
        # right-clicked
        while True:
            (x, y) = self.target_tile(max_range)
            if x is None:
                return None

            # Return the first clicked monster, otherwise continue looking
            for object in self.objects:
                if object.fighter and object != self.player:
                    if object.x == x and object.y == y:
                        return object
