from collections import deque
from pyro.engine.log import Log


class Stage:
    def __init__(self, map_=None, actors=None, items=None):
        self.map = map_
        self.actors = actors
        self.items = items
        self.corpses = []
        self.current_actor_index = 0

    def current_actor(self):
        return self.actors[self.current_actor_index]

    def advance_actor(self):
        self.current_actor_index = (self.current_actor_index + 1) % len(self.actors)

    def remove_actor(self, actor):
        index = self.actors.index(actor)
        if self.current_actor_index > index:
            self.current_actor_index -= 1
        self.actors.pop(index)
        if self.current_actor_index >= len(self.actors):
            self.current_actor_index = 0


class Game:
    def __init__(self, state, dungeon_level):
        self.state = state
        self.stage = None
        self.dungeon_level = dungeon_level
        self.log = Log()
        self.actions = deque()
        self.player = None

    def update(self):
        game_result = GameResult()
        while True:
            # Process any ongoing or pending actions
            while len(self.actions) > 0:
                action = self.actions[0]
                result = action.perform(game_result)

                # Cascade through alternates until we hit bottom
                while result.alternate:
                    self.actions.popleft()
                    action = result.alternate
                    self.actions.appendleft(action)
                    result = action.perform(game_result)

                self.stage.map.refresh_visibility(self.player.pos)
                game_result.made_progress = True

                if result.done:
                    self.actions.popleft()
                    if result.succeeded and action.consumes_energy:
                        action.actor.finish_turn(action)
                        self.stage.advance_actor()

                    # Refresh every time the hero takes a turn
                    if action.actor == self.player:
                        return game_result

                if len(game_result.events) > 0:
                    return game_result

            # If we get here, all pending actions are done, so advance
            # to the next tick until an actor moves
            while len(self.actions) == 0:
                actor = self.stage.current_actor()

                # If we are still waiting for input for the actor, just return (again)
                if actor.energy.can_take_turn() and actor.needs_input():
                    return game_result

                if actor.energy.can_take_turn() or actor.energy.gain(actor.speed()):
                    # If the actor can move now, but needs input from the user, just
                    # return so we can wait for it
                    if actor.needs_input():
                        return game_result

                    self.actions.append(actor.get_action())
                else:
                    # This actor doesn't have enough energy yet, so move on to the next
                    self.stage.advance_actor()


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
    DEATH = None
    HIT = None
    def __init__(self, name):
        self.name = name

EventType.BOLT = EventType('bolt')
EventType.DEATH = EventType('death')
EventType.HIT = EventType('hit')
