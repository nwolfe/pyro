from pyro.engine import Actor
from pyro.engine.attack import Hit


class Hero(Actor):
    def __init__(self, game):
        Actor.__init__(self, game)
        self.next_action = None

    def needs_input(self):
        return self.next_action is None

    def on_get_action(self):
        action = self.next_action
        self.next_action = None
        return action

    def on_create_melee_hit(self):
        return Hit()
