import libtcodpy as libtcod
from pyro.component import Component
from pyro.components.ai import AI
from pyro.components.item import get_all_equipped


class Fighter(Component):
    """Combat-related properties and methods (monster, player, NPC)."""
    def __init__(self, hp, defense, power, death_fn=None):
        Component.__init__(self)
        self.hp = hp
        self.base_max_hp = hp
        self.base_defense = defense
        self.base_power = power
        self.death_fn = death_fn

    def power(self):
        equipped = get_all_equipped(self.owner)
        bonus = sum(equipment.power_bonus for equipment in equipped)
        return self.base_power + bonus

    def defense(self):
        equipped = get_all_equipped(self.owner)
        bonus = sum(equipment.defense_bonus for equipment in equipped)
        return self.base_defense + bonus

    def max_hp(self):
        equipped = get_all_equipped(self.owner)
        bonus = sum(equipment.max_hp_bonus for equipment in equipped)
        return self.base_max_hp + bonus

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage

        # Check for death and call the death function if there is one
        if self.hp <= 0 and self.death_fn:
            self.death_fn(self.owner, self.owner.game)

        # Notify the AI that we were hit
        ai = self.owner.component(AI)
        if ai:
            ai.take_damage(damage)

    def heal(self, amount):
        # Heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp():
            self.hp = self.max_hp()

    def attack(self, target):
        if libtcod.random_get_int(0, 1, 10) == 1:
            msg = '{0} attacks {1} but misses!'.format(
                self.owner.name.capitalize(), target.name)
            self.owner.game.message(msg)
            return

        fighter = target.component(Fighter)
        damage = self.power() - fighter.defense()

        if damage > 0:
            msg = '{0} attacks {1} for {2} hit points.'.format(
                self.owner.name.capitalize(), target.name, damage)
            if self.owner == self.owner.game.player:
                self.owner.game.message(msg, libtcod.light_green)
            else:
                self.owner.game.message('- ' + msg, libtcod.light_red)
            fighter.take_damage(damage)
        else:
            msg = '{0} attacks {1} but it has no effect!'.format(
                self.owner.name.capitalize(), target.name)
            self.owner.game.message(msg)
