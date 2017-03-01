import libtcodpy as libtcod
from pyro.components.fighter import Fighter
from pyro.components.projectile import TargetProjectile, PositionProjectile
from pyro.gameobject import GameObject
from pyro.spell import Spell


class Fireball(Spell):
    def __init__(self):
        Spell.__init__(self, 'Fireball', spell_range=4, strength=25)
        self.radius = 3

    def initialize_monster(self):
        self.strength = 15
        self.radius = 2

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