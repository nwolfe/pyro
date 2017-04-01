from pyro.components import Fighter
from pyro.engine import Event, EventType
from pyro.engine.actions import Action, ActionResult


class AttackAction(Action):
    def __init__(self, defender):
        Action.__init__(self)
        self.defender = defender

    def on_perform(self):
        # TODO Use a Hit instead
        # hit = self.actor.create_melee_hit()
        # hit.perform(self, self.actor, self.defender)
        self.actor.game.player.component(Fighter).attack(self.defender)
        self.add_event(Event(EventType.HIT, actor=self.defender))
        return ActionResult.SUCCESS
