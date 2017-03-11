import tcod as libtcod
from pyro.components import AI, Movement
from pyro.ai import Aggressive
from pyro.events import EventListener


class PassiveAggressive(AI, EventListener):
    """Neutral, until the player attacks. May wander in a random direction."""

    def set_owner(self, game_object):
        AI.set_owner(self, game_object)
        game_object.add_event_listener(self)

    def remove_owner(self, game_object):
        game_object.remove_event_listener(self)

    def handle_event(self, source, event, context):
        if event == 'take_damage':
            source.set_component(Aggressive())

    def take_turn(self):
        # 25% chance to move one square in a random direction
        if libtcod.random_get_int(0, 1, 4) == 1:
            movement = self.owner.component(Movement)
            if movement:
                movement.move(libtcod.random_get_int(0, -1, 1),
                              libtcod.random_get_int(0, -1, 1))
