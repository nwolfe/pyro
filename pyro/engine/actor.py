import abc
from pyro.energy import Energy, NORMAL_SPEED
from pyro.engine import Event, EventType
from pyro.components.item import get_all_equipped


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
            action.bind(self, True)
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
        equipped = get_all_equipped(self)
        bonus = sum(equipment.power_bonus for equipment in equipped)
        return self.game_object.__base_power__ + bonus

    @property
    def defense(self):
        equipped = get_all_equipped(self)
        bonus = sum(equipment.defense_bonus for equipment in equipped)
        return self.game_object.__base_defense__ + bonus

    @property
    def hp(self):
        return self.game_object.__hp__

    @property
    def max_hp(self):
        equipped = get_all_equipped(self)
        bonus = sum(equipment.max_hp_bonus for equipment in equipped)
        return self.game_object.__base_max_hp__ + bonus

    def take_damage(self, action, damage, attacker):
        if damage > 0:
            self.game_object.__hp__ -= damage

        if self.game_object.__hp__ <= 0:
            action.add_event(Event(EventType.DEATH, actor=self, other=attacker))

    def heal(self, amount):
        # Heal by the given amount, without going over the maximum
        self.game_object.__hp__ += amount
        if self.game_object.__hp__ > self.max_hp:
            self.game_object.__hp__ = self.max_hp

    def is_alive(self):
        return self.hp > 0

    # Temporary bridge so Actor can be used in place of a GameObject.
    # Remove once game.objects is all Actors; monsters are Monsters.
    @property
    def actor(self):
        return self
