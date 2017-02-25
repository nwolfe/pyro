import libtcodpy as libtcod
from pyro.components.ai import AI
from pyro.components.fighter import Fighter
from pyro.components.projectile import TargetProjectile, PositionProjectile
from pyro.gameobject import GameObject
from pyro.ai.confused import Confused
from pyro.settings import *


class Spell:
    def __init__(self, name, spell_range, strength):
        self.name = name
        self.range = spell_range
        self.strength = strength

    def initialize_monster(self):
        pass

    def cast(self, caster, target):
        pass

    def player_cast(self, player, game, ui):
        pass


class LightningBolt(Spell):
    def __init__(self):
        Spell.__init__(self, 'Lightning Bolt', LIGHTNING_RANGE, LIGHTNING_DAMAGE)

    def initialize_monster(self):
        self.strength = 5

    def cast(self, caster, target):
        def on_hit(source, t):
            t.component(Fighter).take_damage(self.strength)
        bolt = TargetProjectile(source=caster, target=target, on_hit_fn=on_hit)
        obj = GameObject(name='Bolt of Lightning', glyph='*',
                         components=[bolt],
                         color=libtcod.blue, blocks=False, game=caster.game)
        caster.game.add_object(obj)

    def player_cast(self, player, game, ui):
        # Find the closest enemy (inside a maximum range) and damage it
        monster = game.closest_monster(self.range)
        if monster is None:
            game.message('No enemy is close enough to strike.', libtcod.red)
            return 'cancelled'

        # Zap it!
        msg = 'A lightning bolt strikes the {0} with a loud thunderclap! '
        msg += 'The damage is {1} hit points.'
        msg = msg.format(monster.name, self.strength)
        game.message(msg, libtcod.light_blue)
        self.cast(player, monster)


class Heal(Spell):
    def __init__(self):
        Spell.__init__(self, 'Healing', spell_range=0, strength=HEAL_AMOUNT)

    def cast(self, caster, target):
        target.component(Fighter).heal(self.strength)

    def player_cast(self, player, game, ui):
        # Heal the player
        fighter = player.component(Fighter)
        if fighter.hp == fighter.max_hp():
            game.message('You are already at full health.', libtcod.red)
            return 'cancelled'

        game.message('Your wounds start to feel better!', libtcod.light_violet)
        self.cast(player, player)


class Confuse(Spell):
    def __init__(self):
        Spell.__init__(self, 'Confusion', CONFUSE_RANGE, strength=0)

    def cast(self, caster, target):
        old_ai = target.component(AI)
        new_ai = Confused(old_ai)
        target.set_component(new_ai)

    def player_cast(self, player, game, ui):
        # Ask the player for a target to confuse
        game.message('Left-click an enemy to confuse it, or right-click to cancel.',
                     libtcod.light_cyan)
        monster = game.target_monster(ui, self.range)
        if monster is None:
            return 'cancelled'

        self.cast(player, monster)
        msg = 'The eyes of the {0} look vacant as he starts to stumble around!'
        game.message(msg.format(monster.name), libtcod.light_green)


class Fireball(Spell):
    def __init__(self):
        Spell.__init__(self, 'Fireball', spell_range=4, strength=FIREBALL_DAMAGE)
        self.radius = FIREBALL_RADIUS

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
                        fighter.take_damage(self.strength)
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
                        fighter.take_damage(self.strength)
        fireball = PositionProjectile(source=player, target_x=x, target_y=y, on_hit_fn=on_hit)
        obj = GameObject(name='Fireball', glyph='@', color=libtcod.dark_orange,
                         components=[fireball], blocks=False,
                         game=game)
        game.add_object(obj)
