from pyro.components import AI
from pyro.energy import Energy, NORMAL_SPEED


class Actor:
    def __init__(self, game, pos):
        self.energy = Energy()
        self.game = game
        self.pos = pos

    def needs_input(self):
        return False

    def speed(self):
        return NORMAL_SPEED

    def get_action(self):
        action = self.on_get_action()
        if action:
            action.bind(self)
        return action

    def on_get_action(self):
        return None

    def finish_turn(self, action):
        self.energy.spend()


class Hero(Actor):
    def __init__(self, hero_object, game):
        Actor.__init__(self, game, None)
        self.hero_object = hero_object
        self.next_action = None

    def needs_input(self):
        return self.next_action is None

    def on_get_action(self):
        action = self.next_action
        self.next_action = None
        return action


class Monster(Actor):
    def __init__(self, monster_object, game):
        Actor.__init__(self, game, None)
        self.monster_object = monster_object

    def on_get_action(self):
        return AIAdapterAction(self.monster_object.component(AI))


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
        return self.on_perform()

    def on_perform(self):
        pass

    def add_event(self, event):
        self.game_result.events.append(event)

    def alternate(self, action):
        action.bind(self.actor)
        return ActionResult(alternate=action)


# class LosAction(Action):
#     def __init__(self, target_x, target_y):
#         Action.__init__(self)
#         self.target_x = target_x
#         self.target_y = target_y
#
#     # def on_perform(self):


class AIAdapterAction(Action):
    def __init__(self, monster_ai):
        Action.__init__(self)
        self.monster_ai = monster_ai

    def on_perform(self):
        if self.monster_ai:
            self.monster_ai.take_turn()
        return ActionResult.SUCCESS


class ActionResult:
    SUCCESS = None
    FAILURE = None
    def __init__(self, succeeded=False, alternate=None):
        self.succeeded = succeeded
        self.alternate = alternate

ActionResult.SUCCESS = ActionResult(succeeded=True)
ActionResult.FAILURE = ActionResult(succeeded=False)


class GameResult:
    def __init__(self):
        self.events = []
        self.made_progress = False

    def needs_refresh(self):
        return self.made_progress or len(self.events) > 0


class Event:
    def __init__(self, kind, pos):
        self.type = kind
        self.pos = pos


class EventType:
    BOLT = None
    HIT = None
    def __init__(self, name):
        self.name = name

EventType.BOLT = EventType('bolt')
EventType.HIT = EventType('hit')


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
