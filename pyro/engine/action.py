import abc


class Action:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.actor = None
        self.game = None
        self.game_result = None
        self.consumes_energy = None

    def bind(self, actor, consumes_energy):
        self.actor = actor
        self.game = actor.game
        self.consumes_energy = consumes_energy

    def perform(self, game_result):
        self.game_result = game_result
        return self.on_perform()

    @abc.abstractmethod
    def on_perform(self):
        pass

    def add_event(self, event):
        self.game_result.events.append(event)

    def alternate(self, action):
        action.bind(self.actor, self.consumes_energy)
        return ActionResult(alternate=action)

    def succeed(self):
        return ActionResult.SUCCESS

    def fail(self):
        return ActionResult.FAILURE


class ActionResult:
    SUCCESS = None
    FAILURE = None
    def __init__(self, succeeded=False, alternate=None, done=True):
        self.succeeded = succeeded
        self.alternate = alternate
        self.done = done

ActionResult.SUCCESS = ActionResult(succeeded=True)
ActionResult.FAILURE = ActionResult(succeeded=False)
