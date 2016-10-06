

class Component:
    def __init__(self):
        self.owner = None

    def initialize(self, object):
        self.owner = object

    def handle_event(self, event):
        return
