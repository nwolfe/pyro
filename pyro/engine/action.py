import abc


class Action:
    __metaclass__ = abc.ABCMeta

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

    @abc.abstractmethod
    def on_perform(self):
        pass

    def add_event(self, event):
        self.game_result.events.append(event)

    def alternate(self, action):
        action.bind(self.actor)
        return ActionResult(alternate=action)


class ActionResult:
    SUCCESS = None
    FAILURE = None
    def __init__(self, succeeded=False, alternate=None):
        self.succeeded = succeeded
        self.alternate = alternate

ActionResult.SUCCESS = ActionResult(succeeded=True)
ActionResult.FAILURE = ActionResult(succeeded=False)
