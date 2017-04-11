from pyro.components import Fighter
from pyro.engine import Action, ActionResult, Event, EventType


class AttackAction(Action):
    def __init__(self, defender):
        Action.__init__(self)
        self.defender = defender

    def on_perform(self):
        # TODO Use a Hit instead
        # hit = self.actor.create_melee_hit()
        # hit.perform(self, self.actor, self.defender)
        self.actor.game_object.component(Fighter).attack(self, self.defender.game_object)
        self.add_event(Event(EventType.HIT, actor=self.defender))
        return ActionResult.SUCCESS
