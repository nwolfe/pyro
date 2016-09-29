import component as libcomp
import item as libitem
import ai as libai


class Fighter(libcomp.Component):
    """Combat-related properties and methods (monster, player, NPC)."""
    def __init__(self, hp, defense, power, death_fn=None):
        self.hp = hp
        self.base_max_hp = hp
        self.base_defense = defense
        self.base_power = power
        self.death_fn = death_fn

    def power(self):
        equipped = libitem.get_all_equipped(self.owner)
        bonus = sum(equipment.power_bonus for equipment in equipped)
        return self.base_power + bonus

    def defense(self):
        equipped = libitem.get_all_equipped(self.owner)
        bonus = sum(equipment.defense_bonus for equipment in equipped)
        return self.base_defense + bonus

    def max_hp(self):
        equipped = libitem.get_all_equipped(self.owner)
        bonus = sum(equipment.max_hp_bonus for equipment in equipped)
        return self.base_max_hp + bonus

    def take_damage(self, damage, game):
        if damage > 0:
            self.hp -= damage

        # Check for death and call the death function if there is one
        if self.hp <= 0 and self.death_fn:
            self.death_fn(self.owner, game)

        # Notify the AI that we were hit
        ai = self.owner.components.get(libai.AI)
        if ai:
            ai.take_damage(damage, game)

    def heal(self, amount):
        # Heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp():
            self.hp = self.max_hp()

    def attack(self, target, game):
        fighter = target.components.get(Fighter)
        damage = self.power() - fighter.defense()

        if damage > 0:
            game.message('{0} attacks {1} for {2} hit points.'.format(
                self.owner.name.capitalize(), target.name, damage))
            fighter.take_damage(damage, game)
        else:
            game.message('{0} attacks {1} but it has no effect!'.format(
                self.owner.name.capitalize(), target.name))
