import tcod as libtcod
from pyro.spell import Spell
from pyro.settings import SPELL_CONFUSE_RANGE, SPELL_CONFUSE_TURNS


class Confuse(Spell):
    def __init__(self):
        Spell.__init__(self, 'Confusion', Spell.TYPE_ATTACK)
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
                msg = 'The eyes of the {0} look vacant as he starts to stumble around!'
                action.game.log.message(msg.format(target.name), libtcod.light_green)
            target.ai.confuse(self.num_turns)
