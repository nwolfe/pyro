import abc
from pyro.energy import Energy, NORMAL_SPEED
from pyro.engine.game import Event
from pyro.position import Position
from pyro.settings import LEVEL_UP_BASE, LEVEL_UP_FACTOR


class Actor:
    __metaclass__ = abc.ABCMeta

    def __init__(self, game):
        self.name = None
        self.glyph = None
        self._pos = Position()
        self.energy = Energy()
        self.game = game
        self.hp = 0
        self.base_max_hp = 0
        self.base_defense = 0
        self.base_power = 0
        self.xp = 0
        self.level = 1
        self.inventory = None

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, other):
        if self._pos != other:
            self._pos.copy(other)

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
    def power(self):
        bonus = 0
        if self.inventory:
            equipped = filter(lambda i: i.is_equipped, self.inventory)
            bonus = sum(equipment.power_bonus for equipment in equipped)
        return self.base_power + bonus

    @property
    def defense(self):
        bonus = 0
        if self.inventory:
            equipped = filter(lambda i: i.is_equipped, self.inventory)
            bonus = sum(equipment.defense_bonus for equipment in equipped)
        return self.base_defense + bonus

    @property
    def max_hp(self):
        bonus = 0
        if self.inventory:
            equipped = filter(lambda i: i.is_equipped, self.inventory)
            bonus = sum(equipment.max_hp_bonus for equipment in equipped)
        return self.base_max_hp + bonus

    def take_damage(self, action, damage, attacker):
        self.hp -= damage
        self.on_damaged(action, damage, attacker)

        if self.hp <= 0:
            action.add_event(Event(Event.TYPE_DEATH, actor=self, other=attacker))
            attacker.on_killed(self)
            self.on_death(attacker)

    def on_damaged(self, action, damage, attacker):
        pass

    def on_death(self, attacker):
        pass

    def on_killed(self, defender):
        pass

    def heal(self, amount):
        # Heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_alive(self):
        return self.hp > 0

    def required_for_level_up(self):
        return LEVEL_UP_BASE + self.level * LEVEL_UP_FACTOR

    def can_level_up(self):
        return self.xp >= self.required_for_level_up()

    def level_up(self):
        required = self.required_for_level_up()
        self.level += 1
        self.xp -= required

    def is_player(self):
        return self == self.game.player
