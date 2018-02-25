import tcod as libtcod
from pyro.engine import Action, Event
from pyro.spell import Spell, CastResult
from pyro.settings import SPELL_HEAL_STRENGTH


class Heal(Spell):
    def __init__(self):
        Spell.__init__(self, 'Healing', Spell.TYPE_HEAL)
        self.strength = SPELL_HEAL_STRENGTH

    def configure(self, settings):
        self.strength = settings.get('strength', self.strength)

    def in_range(self, caster, target):
        return caster.pos == target.pos

    def cast(self, action, caster, target):
        if caster.is_player():
            if caster.hp == caster.max_hp:
                action.game.log.message('You are already at full health.', libtcod.red)
                return CastResult.cancel()
            else:
                action.game.log.message('Your wounds start to feel better!', libtcod.light_violet)
                caster.heal(self.strength)
                return CastResult.hit(self.strength)
        else:
            target.actor.heal(self.strength)
            return CastResult.hit(self.strength)

    def requires_target(self):
        return False

    def cast_action(self, target):
        return HealAction(self.strength)


class HealAction(Action):
    def __init__(self, amount):
        Action.__init__(self)
        self._amount = amount

    def on_perform(self):
        """Heal the caster. Prints messages that assume caster is player."""
        caster = self.actor
        if (caster.hp < caster.max_hp) and self._amount > 0:
            caster.heal(self._amount)
            self.add_event(Event(Event.TYPE_HEAL, actor=caster))
            self.game.log.message('Your wounds start to feel better!', libtcod.light_violet)
        else:
            self.game.log.message("You don't feel any different.")
        return self.succeed()
