from pyro.engine import Actor


class Hero(Actor):
    def __init__(self, hero_object, game):
        Actor.__init__(self, game)
        self.hero_object = hero_object
        self.next_action = None

    def needs_input(self):
        return self.next_action is None

    def on_get_action(self):
        action = self.next_action
        self.next_action = None
        return action
