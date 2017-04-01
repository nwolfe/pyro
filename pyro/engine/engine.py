

class GameEngine:
    def __init__(self, actors):
        self.actors = actors if actors else []
        self.current_actor_index = 0
        self.spend_energy_on_failure = True
        self.stop_after_every_process = False

    def update(self):
        game_result = GameResult()
        while True:
            actor = self.__current_actor__()
            # If we are still waiting for input for the actor, just return
            if actor.energy.can_take_turn() and actor.needs_input():
                return game_result
            game_result.made_progress = True
            # All pending actions are done, so advance to the next tick
            # until an actor moves
            action = None
            while action is None:
                actor = self.__current_actor__()
                if actor.energy.can_take_turn() or actor.energy.gain(actor.speed()):
                    # If the actor can move now, but needs input from the user, just
                    # return so we can wait for it
                    if actor.needs_input():
                        return game_result
                    action = actor.get_action()
                else:
                    # This actor doesn't have enough energy yet, so move on to the next
                    self.__advance_actor__()
                    if self.stop_after_every_process:
                        return game_result

            # Cascade through the alternates until none left
            action_result = action.perform(game_result)
            while action_result.alternate:
                action = action_result.alternate
                action_result = action.perform(game_result)

            if self.spend_energy_on_failure or action_result.succeeded:
                action.actor.finish_turn(action)
                self.__advance_actor__()

    def __current_actor__(self):
        return self.actors[self.current_actor_index]

    def __advance_actor__(self):
        self.current_actor_index = (self.current_actor_index + 1) % len(self.actors)


class GameResult:
    def __init__(self):
        self.events = []
        self.made_progress = False

    def needs_refresh(self):
        return self.made_progress or len(self.events) > 0


class Event:
    def __init__(self, kind, actor=None, position=None, direction=None, other=None):
        self.type = kind
        self.actor = actor
        self.position = position
        self.direction = direction
        self.other = other


class EventType:
    BOLT = None
    HIT = None
    def __init__(self, name):
        self.name = name

EventType.BOLT = EventType('bolt')
EventType.HIT = EventType('hit')

