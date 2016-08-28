import libtcodpy as libtcod
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
                 map=None,
                 fov_map=None,
                 objects=None,
                 player=None,
                 messages=None):
        self.state = state
        self.map = map
        self.fov_map = fov_map
        self.objects = objects
        self.player = player
        self.messages = messages
