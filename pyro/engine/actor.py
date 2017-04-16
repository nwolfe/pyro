import abc
from pyro.energy import Energy, NORMAL_SPEED


class Actor:
    __metaclass__ = abc.ABCMeta

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

    @abc.abstractmethod
    def on_get_action(self):
        pass

    def finish_turn(self, action):
        self.energy.spend()

    def create_melee_hit(self):
        hit = self.on_create_melee_hit()
        self.modify_hit(hit)
        return hit

    @abc.abstractmethod
    def on_create_melee_hit(self):
        pass

    def modify_hit(self, hit):
        self.on_modify_hit(hit)

    def on_modify_hit(self, hit):
        pass

    @property
    def pos(self):
        return self.game_object.pos

    @property
    def name(self):
        return self.game_object.name

    @property
    def power(self):
        return self.game_object.power

    @property
    def defense(self):
        return self.game_object.defense

    def take_damage(self, action, damage, attacker):
        self.game_object.take_damage(action, damage, attacker)

