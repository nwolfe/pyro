import tcod as libtcod
from pyro.spell import Spell
from pyro.settings import SPELL_FIREBALL_RANGE, SPELL_FIREBALL_STRENGTH, SPELL_FIREBALL_RADIUS


class Fireball(Spell):
    def __init__(self):
        Spell.__init__(self, 'Fireball', Spell.TYPE_ATTACK)
        self.range = SPELL_FIREBALL_RANGE
        self.strength = SPELL_FIREBALL_STRENGTH
        self.radius = SPELL_FIREBALL_RADIUS

    def configure(self, settings):
        self.range = settings.get('range', self.range)
        self.strength = settings.get('strength', self.strength)
        self.radius = settings.get('radius', self.radius)

    def in_range(self, caster, target):
        return caster.pos.distance_to(target.pos) <= self.range

    def cast(self, action, caster, target):
        # TODO Condition behavior when caster is player
        action.game.log.message('The fireball explodes, burning everything within {0} tiles!'.
                                format(self.radius), libtcod.orange)
        for game_object in action.game.stage.actors:
            if game_object.pos.distance(target.pos.x, target.pos.y) <= self.radius:
                action.game.log.message('The {0} gets burned for {1} hit points.'.
                                        format(game_object.name, self.strength), libtcod.orange)
                game_object.take_damage(action, self.strength, caster)
        return self.strength
