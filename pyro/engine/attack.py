import tcod as libtcod
from pyro.engine.game import Event


class Attack:
    # TODO Add params: damage, range (optional), element (optional)
    def __init__(self, noun, verb):
        """Noun is a Noun, verb is a String"""
        self.noun = noun
        self.verb = verb

    def create_hit(self):
        return Hit(self)


class Hit:
    def __init__(self, attack=None):
        self._attack = attack

    def perform(self, action, attacker, defender, can_miss=True):
        attack_noun = attacker
        attack_verb = 'attack[s]'
        if self._attack:
            if self._attack.noun:
                attack_noun = self._attack.noun
            if self._attack.verb:
                attack_verb = self._attack.verb

        if can_miss:
            if libtcod.random_get_int(0, 1, 10) == 1:
                action.log('{1} %s {2} but miss[es]!' % attack_verb, attack_noun, defender)
                return

        # TODO armor, resistances, etc.
        damage = attacker.power - defender.defense

        if damage <= 0:
            action.log('{1} do[es] no damage to {2}.', attack_noun, defender)
            return

        action.add_event(Event(Event.TYPE_HIT, actor=defender))
        action.log('{1} %s {2} for %d damage!' % (attack_verb, damage), attack_noun, defender)

        attacker.on_give_damage(action, defender, damage)
        defender.take_damage(action, damage, attacker)

