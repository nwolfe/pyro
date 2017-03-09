import tcod as libtcod
from pyro.components import Fighter, TargetProjectile, PositionProjectile
from pyro.gameobject import GameObject
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
        return caster.distance_to(target) <= self.range

    def cast(self, caster, target):
        def on_hit(source, t):
            source.game.message('The fireball explodes, burning everything within {0} tiles!'.
                                format(self.radius), libtcod.orange)
            for game_object in source.game.objects:
                if game_object.distance(t.x, t.y) <= self.radius:
                    fighter = game_object.component(Fighter)
                    if fighter:
                        source.game.message('The {0} gets burned for {1} hit points.'.format(
                            game_object.name, self.strength), libtcod.orange)
                        fighter.take_damage(self.strength, source)
        fireball = TargetProjectile(source=caster, target=target, on_hit_fn=on_hit)
        obj = GameObject(name='Fireball', glyph='@', color=libtcod.dark_orange,
                         components=[fireball], blocks=False,
                         game=caster.game)
        caster.game.add_object(obj)
        return self.strength

    def player_cast(self, player, game, ui):
        # Ask the player for a target tile to throw a fireball at
        msg = 'Left-click a target tile for the fireball, or right-click to cancel.'
        game.message(msg, libtcod.light_cyan)
        (x, y) = game.target_tile(ui)
        if x is None:
            return 'cancelled'

        def on_hit(source, target_x, target_y):
            source.game.message('The fireball explodes, burning everything within {0} tiles!'.
                                format(self.radius), libtcod.orange)
            for game_object in game.objects:
                if game_object.distance(target_x, target_y) <= self.radius:
                    fighter = game_object.component(Fighter)
                    if fighter:
                        game.message('The {0} gets burned for {1} hit points.'.format(
                            game_object.name, self.strength), libtcod.orange)
                        fighter.take_damage(self.strength, source)
        fireball = PositionProjectile(source=player, target_x=x, target_y=y, on_hit_fn=on_hit)
        obj = GameObject(name='Fireball', glyph='@', color=libtcod.dark_orange,
                         components=[fireball], blocks=False,
                         game=game)
        game.add_object(obj)
