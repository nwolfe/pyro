import tcod as libtcod
from textwrap import wrap
from pyro.utilities import is_blocked
from pyro.settings import MSG_WIDTH, MSG_HEIGHT


class Game:
    def __init__(self,
                 state=None,
                 map=None,
                 objects=None,
                 player=None,
                 messages=None,
                 dungeon_level=1):
        self.state = state
        self.map = map
        self.objects = objects
        self.player = player
        self.messages = messages
        self.dungeon_level = dungeon_level
        self.actors = None

        if self.messages is None:
            self.messages = []

    def add_object(self, game_object):
        self.objects.append(game_object)

    def remove_object(self, game_object):
        if game_object in self.objects:
            self.objects.remove(game_object)

    def is_blocked(self, position):
        return is_blocked(self.map, self.objects, position.x, position.y)

    def message(self, text, color=libtcod.white):
        # Split the message if necessary, among multiple lines
        new_msg_lines = wrap(text, MSG_WIDTH)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room
            if len(self.messages) == MSG_HEIGHT:
                del self.messages[0]

            # Add the new line as a tuple, with the text and color
            self.messages.append((line, color))
