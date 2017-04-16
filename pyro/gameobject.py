import tcod as libtcod
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
            action.add_event(Event(EventType.DEATH, actor=self, other=attacker))

    def attack(self, action, defender):
        if libtcod.random_get_int(0, 1, 10) == 1:
            msg = '{0} attacks {1} but misses!'.format(self.name, defender.name)
            self.game.message(msg)
            return

        damage = self.power - defender.defense

        if damage > 0:
            msg = '{0} attacks {1} for {2} hit points.'.format(
                self.name, defender.name, damage)
            if self == self.game.player:
                self.game.message(msg, libtcod.light_green)
            else:
                self.game.message('- ' + msg, libtcod.light_red)
            defender.take_damage(action, damage, self)
        else:
            msg = '{0} attacks {1} but it has no effect!'.format(
                self.name, defender.name)
            self.game.message(msg)

    def raise_base_max_hp(self, value):
        self.base_max_hp += value

    def raise_hp(self, value):
        self.hp += value

    def raise_base_power(self, value):
        self.base_power += value

    def raise_base_defense(self, value):
        self.base_defense += value

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
