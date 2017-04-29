import tcod as libtcod
from textwrap import wrap
from pyro.settings import MSG_WIDTH, MSG_HEIGHT


class Log:
    def __init__(self, messages=None):
        self.messages = messages or []

    def message(self, text, color=libtcod.white):
        # Split the message if necessary, among multiple lines
        new_msg_lines = wrap(text, MSG_WIDTH)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room
            if len(self.messages) == MSG_HEIGHT:
                del self.messages[0]

            # Add the new line as a tuple, with the text and color
            self.messages.append((line, color))
