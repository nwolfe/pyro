import libtcodpy as libtcod
from pyro.components.ai import AI
from pyro.components.fighter import Fighter
from pyro.components.projectile import Projectile, TargetProjectile, PositionProjectile
from pyro.gameobject import GameObject
from pyro.ai.confused import Confused
from pyro.settings import *


class Spell:
    def __init__(self, name, spell_range, strength):
        self.name = name
        self.base_range = spell_range
        self.base_strength = strength

    def range(self):
        return self.base_range

    def strength(self):
        return self.base_strength

    def cast(self, caster, target):
        pass

    def player_cast(self, player, game, ui):
        pass

    def initialize_player(self):
        pass

    def initialize_monster(self):
        pass


class LightningBolt(Spell):
    def __init__(self, name='Lightning Bolt', spell_range=LIGHTNING_RANGE,
                 strength=LIGHTNING_DAMAGE):
        Spell.__init__(self, name, spell_range, strength)

    def cast(self, caster, target):
        def on_hit(source, t):
            t.component(Fighter).take_damage(self.strength())
        bolt = TargetProjectile(source=caster, target=target, on_hit_fn=on_hit)
        obj = GameObject(name='Bolt of Lightning', glyph='*',
                         components={Projectile: bolt},
                         color=libtcod.blue, blocks=False, game=caster.game)
        caster.game.objects.append(obj)

    def player_cast(self, player, game, ui):
        # Find the closest enemy (inside a maximum range) and damage it
        monster = game.closest_monster(self.range())
        if monster is None:
            game.message('No enemy is close enough to strike.', libtcod.red)
            return 'cancelled'

        # Zap it!
        msg = 'A lightning bolt strikes the {0} with a loud thunderclap! '
        msg += 'The damage is {1} hit points.'
        msg = msg.format(monster.name, self.strength())
        game.message(msg, libtcod.light_blue)
        self.cast(player, monster)

    def initialize_monster(self):
        self.base_strength = 5


class Heal(Spell):
    def __init__(self, name='Healing', strength=HEAL_AMOUNT):
        Spell.__init__(self, name, 0, strength)

    def cast(self, caster, target):
        target.component(Fighter).heal(self.strength())

    def player_cast(self, player, game, ui):
        # Heal the player
        fighter = player.component(Fighter)
        if fighter.hp == fighter.max_hp():
            game.message('You are already at full health.', libtcod.red)
            return 'cancelled'

        game.message('Your wounds start to feel better!', libtcod.light_violet)
        self.cast(player, player)


class Confuse(Spell):
    def __init__(self, name='Confusion', spell_range=CONFUSE_RANGE):
        Spell.__init__(self, name, spell_range, 0)

    def cast(self, caster, target):
        old_ai = target.component(AI)
        new_ai = Confused(old_ai)
        target.set_component(AI, new_ai)

    def player_cast(self, player, game, ui):
        # Ask the player for a target to confuse
        game.message('Left-click an enemy to confuse it, or right-click to cancel.',
                     libtcod.light_cyan)
        monster = game.target_monster(ui, self.range())
        if monster is None:
            return 'cancelled'

        self.cast(player, monster)
        msg = 'The eyes of the {0} look vacant as he starts to stumble around!'
        game.message(msg.format(monster.name), libtcod.light_green)


class Fireball(Spell):
    def __init__(self, name='Fireball', spell_range=4, strength=FIREBALL_DAMAGE):
        Spell.__init__(self, name, spell_range, strength)
        self.radius = FIREBALL_RADIUS

    def initialize_monster(self):
        self.base_strength = 15
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
                            game_object.name, self.strength()), libtcod.orange)
                        fighter.take_damage(self.strength())
        fireball = TargetProjectile(source=caster, target=target, on_hit_fn=on_hit)
        obj = GameObject(name='Fireball', glyph='@', color=libtcod.dark_orange,
                         components={Projectile: fireball}, blocks=False,
                         game=caster.game)
        caster.game.objects.append(obj)

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
                            game_object.name, self.strength()), libtcod.orange)
                        fighter.take_damage(self.strength())
        fireball = PositionProjectile(source=player, target_x=x, target_y=y, on_hit_fn=on_hit)
        obj = GameObject(name='Fireball', glyph='@', color=libtcod.dark_orange,
                         components={Projectile: fireball}, blocks=False,
                         game=game)
        game.objects.append(obj)
