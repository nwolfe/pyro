import libtcodpy as libtcod
from pyro.engine import Action, Event
from pyro.spell import Spell
from pyro.settings import SPELL_HEAL_STRENGTH


class Heal(Spell):
    def __init__(self):
        Spell.__init__(self, 'Healing', Spell.TYPE_HEAL)
        self.strength = SPELL_HEAL_STRENGTH

    def configure(self, settings):
        self.strength = settings.get('strength', self.strength)

    def in_range(self, caster, target):
        return caster.pos == target.pos

    def requires_target(self):
        return self.target_self()

    def cast(self, target):
        return HealAction(target, self.strength)


class HealAction(Action):
    def __init__(self, target, amount):
        Action.__init__(self)
        self._target = target
        self._amount = amount

    def on_perform(self):
        """Heal the target, which can be the player or a monster."""
        target = self._target.actor
        if (target.hp < target.max_hp) and self._amount > 0:
            target.heal(self._amount)
            self.add_event(Event(Event.TYPE_HEAL, actor=target))
            self.log('{1} feel[s] better.', target)
        else:
            self.log("{1} [don't|doesn't] feel any different.", target)
        return self.succeed()
