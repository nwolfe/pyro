import libtcodpy as libtcod
from pyro.components.fighter import Fighter
from pyro.components.projectile import TargetProjectile
from pyro.gameobject import GameObject
from pyro.spell import Spell


class LightningBolt(Spell):
    def __init__(self):
        Spell.__init__(self, 'Lightning Bolt', spell_range=5, strength=40)

    def initialize_monster(self):
        self.strength = 5

    def cast(self, caster, target):
        def on_hit(source, t):
            t.component(Fighter).take_damage(self.strength, source)
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
