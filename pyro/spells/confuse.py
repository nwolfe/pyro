import tcod as libtcod
from pyro.engine import Action, Event
from pyro.spell import ActionSpell, CastResult
from pyro.settings import SPELL_CONFUSE_RANGE, SPELL_CONFUSE_TURNS


class Confuse(ActionSpell):
    def __init__(self):
        ActionSpell.__init__(self, 'Confusion', ActionSpell.TYPE_ATTACK)
        self.range = SPELL_CONFUSE_RANGE
        self.num_turns = SPELL_CONFUSE_TURNS

    def configure(self, settings):
        self.range = settings.get('range', self.range)
        self.num_turns = settings.get('turns', self.num_turns)

    def in_range(self, caster, target):
        return caster.pos.distance_to(target.pos) <= self.range

    def cast(self, action, caster, target):
        target = target.actor
        if target:
            if caster.is_player():
                msg = 'The eyes of the {0} look vacant as it stumbles around!'
                action.game.log.message(msg.format(target.name), libtcod.light_green)
            target.ai.confuse(self.num_turns)
            return CastResult.hit(-1)
        else:
            if caster.is_player():
                action.game.log.message('Invalid target.', libtcod.orange)
            return CastResult.invalid_target()

    def cast_action(self, target):
        return ConfuseAction(self.num_turns, target)


class ConfuseAction(Action):
    def __init__(self, num_turns, target):
        """Target is a Target instance rather than an Actor."""
        Action.__init__(self)
        self._num_turns = num_turns
        self._target = target

    def on_perform(self):
        """Confuse the target AI. Assumes the player is caster."""
        target = self._target.actor
        if target:
            target.ai.confuse(self._num_turns)
            self.add_event(Event(Event.TYPE_CONFUSE, actor=target))
            msg = 'The eyes of the {0} look vacant as it stumbles around!'
            self.game.log.message(msg.format(target.name), libtcod.light_green)
        else:
            self.game.log.message('Invalid target.', libtcod.orange)
        return self.succeed()

