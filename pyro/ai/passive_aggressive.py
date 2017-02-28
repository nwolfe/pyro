import libtcodpy as libtcod
from pyro.components.ai import AI
from pyro.ai.aggressive import Aggressive
from pyro.events import EventListener


class PassiveAggressive(AI, EventListener):
    """Neutral, until the player attacks. May wander in a random direction."""

    def set_owner(self, game_object):
        AI.set_owner(self, game_object)
        game_object.add_event_listener(self)

    def remove_owner(self, game_object):
        game_object.remove_event_listener(self)

    def handle_event(self, event, context):
        if event == 'take_damage':
            self.owner.set_component(Aggressive())

    def take_turn(self):
        # 25% chance to move one square in a random direction
        if libtcod.random_get_int(0, 1, 4) == 1:
            self.owner.move(libtcod.random_get_int(0, -1, 1),
                            libtcod.random_get_int(0, -1, 1))
