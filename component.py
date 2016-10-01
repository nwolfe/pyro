

class Component:
    def __init__(self):
        self.owner = None
        self.game = None

    def initialize(self, object):
        self.owner = object
