import tcod as libtcod
from pyro.engine import Actor
from pyro.engine.attack import Hit
import pyro.engine.corpse


class Hero(Actor):
    def __init__(self, game):
        Actor.__init__(self, game)
        self.next_action = None

    def needs_input(self):
        return self.next_action is None

    def on_get_action(self):
        action = self.next_action
        self.next_action = None
        return action

    def on_create_melee_hit(self):
        return Hit()

    def on_death(self, attacker):
        self.game.log.message('You died!')
        self.game.stage.remove_actor(self)
        self.game.stage.corpses.append(pyro.engine.corpse.for_hero(self))

    def on_killed(self, defender):
        self.game.log.message('The {0} is dead! You gain {1} experience points.'.
                              format(defender.name, defender.xp), libtcod.orange)
        self.xp += defender.xp
