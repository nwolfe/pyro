

class Component:
    def __init__(self, component_type=None):
        self.type = component_type
        self.owner = None

    def set_owner(self, game_object):
        self.owner = game_object

    def remove_owner(self, game_object):
        pass
