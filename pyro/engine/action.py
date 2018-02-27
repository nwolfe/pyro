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

    def succeed(self, message=None, noun1=None, noun2=None, noun3=None):
        if message:
            self.log(message, noun1, noun2, noun3)
        return ActionResult.SUCCESS

    def fail(self, message=None, noun1=None, noun2=None, noun3=None):
        if message:
            self.error(message, noun1, noun2, noun3)
        return ActionResult.FAILURE

    def not_done(self):
        return ActionResult.NOT_DONE

    def log(self, message, noun1=None, noun2=None, noun3=None):
        # TODO if !actor.isVisibleToHero return (to eliminate off-screen noise)
        self.game.log.message2(message, noun1, noun2, noun3)

    def error(self, message, noun1=None, noun2=None, noun3=None):
        # TODO if !actor.isVisibleToHero return (to eliminate off-screen noise)
        self.game.log.error(message, noun1, noun2, noun3)


class ActionResult:
    SUCCESS = None
    FAILURE = None
    NOT_DONE = None

    def __init__(self, succeeded=False, alternate=None, done=True):
        self.succeeded = succeeded
        self.alternate = alternate
        self.done = done

ActionResult.SUCCESS = ActionResult(succeeded=True)
ActionResult.FAILURE = ActionResult(succeeded=False)
ActionResult.NOT_DONE = ActionResult(succeeded=True, done=False)
