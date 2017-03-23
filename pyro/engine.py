from pyro.energy import Energy, NORMAL_SPEED


class Event:
    def __init__(self):
        pass


class Actor:
    def __init__(self, game, pos):
        self.energy = Energy()
        self.game = game
        self.pos = pos
        self.needs_input = False
        self.speed = NORMAL_SPEED

    def get_action(self):
        action = self.on_get_action()
        if action:
            action.bind(self)
        return action

    def on_get_action(self):
        return None

    def finish_turn(self, action):
        self.energy.spend()


class Action:
    def __init__(self):
        self.actor = None
        self.game = None
        self.game_result = None

    def bind(self, actor):
        self.actor = actor
        self.game = actor.game

    def perform(self, game_result):
        self.game_result = game_result
        self.on_perform()

    def on_perform(self):
        pass


class ActionResult:
    def __init__(self):
        self.alternative = None
        self.succeeded = False


class GameResult:
    def __init__(self):
        self.events = []
        self.made_progress = False

    def needs_refresh(self):
        return self.made_progress or len(self.events) > 0


class GameEngine:
    def __init__(self):
        self.actors = []
        self.current_actor_index = 0
        self.tiles = []

    def update(self):
        game_result = GameResult()
        while True:
            actor = self.__current_actor__()
            # If we are still waiting for input for the actor, just return
            if actor.energy.can_take_turn() and actor.needs_input:
                return game_result
            game_result.made_progress = True
            # All pending actions are done, so advance to the next tick
            # until an actor moves
            action = None
            while action is None:
                actor = self.__current_actor__()
                if actor.energy.can_take_turn() or actor.energy.gain(actor.speed):
                    # If the actor can move now, but needs input from the user, just
                    # return so we can wait for it
                    if actor.needs_input:
                        return game_result
                    action = actor.get_action()
                else:
                    # This actor doesn't have enough energy yet, so move on to the next
                    self.__advance_actor__()

            # Cascade through the alternatives until none left
            action_result = action.perform(game_result)
            while action_result.alternative:
                action = action_result.alternative
                action_result = action.perform(game_result)

            if action_result.succeeded:
                action.actor.finish_turn(action)
                self.__advance_actor__()

    def __current_actor__(self):
        return self.actors[self.current_actor_index]

    def __advance_actor__(self):
        self.current_actor_index = (self.current_actor_index + 1) % len(self.actors)
