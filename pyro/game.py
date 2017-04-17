import tcod as libtcod
from textwrap import wrap
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

    def message(self, text, color=libtcod.white):
        # Split the message if necessary, among multiple lines
        new_msg_lines = wrap(text, MSG_WIDTH)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room
            if len(self.messages) == MSG_HEIGHT:
                del self.messages[0]

            # Add the new line as a tuple, with the text and color
            self.messages.append((line, color))
