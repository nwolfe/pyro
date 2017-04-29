import pyro.engine.corpse
from pyro.engine import Actor, Action, ActionResult
from pyro.engine.attack import Hit


class Monster(Actor):
    def __init__(self, game):
        Actor.__init__(self, game)
        self.ai = None

    def on_get_action(self):
        # TODO Implement
        return AIAdapterAction(self.ai)

    def on_create_melee_hit(self):
        return Hit()

    def on_damaged(self, action, damage, attacker):
        self.ai.took_damage(action, damage, attacker)

    def on_death(self, attacker):
        # Transform it into a nasty corpse!
        self.game.actors.remove(self)
        self.game.corpses.append(pyro.engine.corpse.for_monster(self))


class AIAdapterAction(Action):
    def __init__(self, monster_ai):
        Action.__init__(self)
        self.monster_ai = monster_ai

    def on_perform(self):
        if self.monster_ai:
            action = self.monster_ai.take_turn(self)
            if action:
                return self.alternate(action)
        return ActionResult.SUCCESS
