from pyro.entity import Entity
from pyro.position import Position
from pyro.engine import Event, EventType
from pyro.components.item import get_all_equipped


class GameObject(Entity):
    def __init__(self, name=None, components=None, game=None,
                 hp=0, defense=0, power=0, is_fighter=False):
        Entity.__init__(self, components)
        self.game = game
        self.pos = Position()
        self.name = name
        self.actor = None
        self.hp = hp
        self.base_max_hp = hp
        self.base_defense = defense
        self.base_power = power
        self.is_fighter = is_fighter

    def heal(self, amount):
        # Heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def take_damage(self, action, damage, attacker):
        if damage > 0:
            self.hp -= damage

        if self.hp <= 0:
            action.add_event(Event(EventType.DEATH, actor=self.actor, other=attacker))

    @property
    def max_hp(self):
        equipped = get_all_equipped(self)
        bonus = sum(equipment.max_hp_bonus for equipment in equipped)
        return self.base_max_hp + bonus

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
