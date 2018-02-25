import tcod as libtcod
from pyro.engine import Event
from pyro.engine.actions import LosAction
from pyro.engine.element import Elements
from pyro.position import Position
from pyro.spell import Spell
from pyro.settings import SPELL_FIREBALL_RANGE, SPELL_FIREBALL_STRENGTH, SPELL_FIREBALL_RADIUS
from pyro.tile import Tile


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

    def cast(self, target):
        return FireballAction(target, self.strength, self.radius)


class FireballAction(LosAction):
    def __init__(self, target, damage, radius):
        LosAction.__init__(self, target)
        self._damage = damage
        self._radius = radius

    def on_step(self, position):
        self.add_event(Event(Event.TYPE_BOLT, element=Elements.FIRE, position=position))

    def on_target(self, target):
        self.game.log.message('The fireball explodes, burning everything within {0} tiles!'.
                              format(self._radius), libtcod.orange)
        for actor in self.game.stage.actors:
            if actor.pos.distance_to(target.pos) <= self._radius:
                self.game.log.message('The {0} gets burned for {1} hit points.'.
                                      format(actor.name, self._damage), libtcod.orange)
                actor.take_damage(self, self._damage, self.actor)

        # Send events for the UI to render the explosion
        hit_on = [Tile.TYPE_FLOOR, Tile.TYPE_TALL_GRASS, Tile.TYPE_CRUSHED_GRASS]
        for x in range(target.pos.x - self._radius, target.pos.x + self._radius + 1):
            for y in range(target.pos.y - self._radius, target.pos.y + self._radius + 1):
                if target.pos.distance(x, y) <= self._radius:
                    if self.game.stage.map.tile_at(x, y).type in hit_on:
                        self.add_event(Event(Event.TYPE_BOLT, element=Elements.FIRE, position=Position(x, y)))
