

class Component:
    def __init__(self):
        self.owner = None

    def initialize(self, game_object):
        self.owner = game_object
