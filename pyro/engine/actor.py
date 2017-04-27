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
        self.hp = 0
        self.base_max_hp = 0
        self.base_defense = 0
        self.base_power = 0

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
        return self.base_power + bonus

    @property
    def defense(self):
        equipped = get_all_equipped(self)
        bonus = sum(equipment.defense_bonus for equipment in equipped)
        return self.base_defense + bonus

    @property
    def max_hp(self):
        equipped = get_all_equipped(self)
        bonus = sum(equipment.max_hp_bonus for equipment in equipped)
        return self.base_max_hp + bonus

    def take_damage(self, action, damage, attacker):
        if damage > 0:
            self.hp -= damage

        if self.hp <= 0:
            action.add_event(Event(EventType.DEATH, actor=self, other=attacker))

    def heal(self, amount):
        # Heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    # Temporary bridge to convert usages over to Actors from GameObjects
    def component(self, component_type):
        return self.game_object.component(component_type)
