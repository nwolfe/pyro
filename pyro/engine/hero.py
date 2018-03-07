import libtcodpy as libtcod
from pyro.engine import Actor
from pyro.engine.attack import Hit
from pyro.engine.log import Pronoun
import pyro.engine.corpse


class Hero(Actor):
    def __init__(self, game):
        Actor.__init__(self, game)
        self.next_action = None

    def noun_text(self):
        # Value is 'you'
        return Pronoun.YOU.subjective

    def pronoun(self):
        return Pronoun.YOU

    def needs_input(self):
        return self.next_action is None

    def on_get_action(self):
        action = self.next_action
        self.next_action = None
        return action

    def on_create_melee_hit(self):
        # TODO later: weapon.attack.createHit() ?
        # TODO new Attack()
        # TODO attack.createHit()
        return Hit()

    def on_death(self, attacker):
        self.game.log.message('{1} died!', self)
        self.game.stage.remove_actor(self)
        self.game.stage.corpses.append(pyro.engine.corpse.for_hero(self))

    def on_killed(self, defender):
        self.game.log.message('{1} is dead! {2} gain %d experience points.'
                              % defender.xp, defender, self)
        self.xp += defender.xp
