import tcod as libtcod
import pyro.utilities
from pyro.spell import Spell, SpellType
from pyro.settings import SPELL_FIREBALL_RANGE, SPELL_FIREBALL_STRENGTH, SPELL_FIREBALL_RADIUS


class Fireball(Spell):
    def __init__(self):
        Spell.__init__(self, 'Fireball', SpellType.ATTACK)
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
        caster.game.log.message('The fireball explodes, burning everything within {0} tiles!'.
                                format(self.radius), libtcod.orange)
        for game_object in caster.game.objects:
            if game_object.pos.distance(target.pos.x, target.pos.y) <= self.radius:
                if game_object.actor.is_alive():
                    caster.game.log.message('The {0} gets burned for {1} hit points.'.
                                            format(game_object.name, self.strength), libtcod.orange)
                    game_object.actor.take_damage(action, self.strength, caster)
        return self.strength

    def player_cast(self, action, player, ui):
        # Ask the player for a target tile to throw a fireball at
        msg = 'Left-click a target tile for the fireball, or right-click to cancel.'
        action.game.log.message(msg, libtcod.light_cyan)
        (x, y) = pyro.utilities.target_tile(action.game, ui)
        if x is None:
            return 'cancelled'

        player.game.log.message('The fireball explodes, burning everything within {0} tiles!'.
                                format(self.radius), libtcod.orange)
        for game_object in action.game.objects:
            if game_object.pos.distance(x, y) <= self.radius:
                if game_object.actor.is_alive():
                    action.game.log.message('The {0} gets burned for {1} hit points.'.
                                            format(game_object.name, self.strength), libtcod.orange)
                    game_object.actor.take_damage(action, self.strength, player)
