from pyro.engine import Action, ActionResult


class AttackAction(Action):
    def __init__(self, defender):
        Action.__init__(self)
        self.defender = defender

    def on_perform(self):
        hit = self.actor.create_melee_hit()
        hit.perform(self, self.actor, self.defender)
        return ActionResult.SUCCESS
