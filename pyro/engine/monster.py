from pyro.components import AI
from pyro.engine import Actor, Action, ActionResult


class Monster(Actor):
    def __init__(self, monster_object, game):
        Actor.__init__(self, game, None)
        self.monster_object = monster_object

    def on_get_action(self):
        # TODO Implement
        return AIAdapterAction(self.monster_object.component(AI))


class AIAdapterAction(Action):
    def __init__(self, monster_ai):
        Action.__init__(self)
        self.monster_ai = monster_ai

    def on_perform(self):
        if self.monster_ai:
            self.monster_ai.take_turn(self)
        return ActionResult.SUCCESS
