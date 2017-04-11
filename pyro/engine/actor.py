from pyro.energy import Energy, NORMAL_SPEED


class Actor:
    def __init__(self, game, game_object):
        self.energy = Energy()
        self.game = game
        self.game_object = game_object

    def needs_input(self):
        return False

    def speed(self):
        return NORMAL_SPEED

    def get_action(self):
        action = self.on_get_action()
        if action:
            action.bind(self)
        return action

    def on_get_action(self):
        return None

    def finish_turn(self, action):
        self.energy.spend()

    def create_melee_hit(self):
        # TODO Implement
        return None

    @property
    def pos(self):
        return self.game_object.pos
