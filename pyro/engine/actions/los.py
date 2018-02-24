import abc
from pyro.astar import astar
from pyro.engine import Action

# This is slightly different than the Hauberk implementation.
#
# Instead of the constructor taking a Position/Vector, this
# takes a Target, which provides a Position abstraction over
# either an Actor or Position.
#
# This was useful to allow the original Target to be passed
# all the way through to the subclasses that actually implement
# game behavior.
#
# Otherwise, the subclass would have to (re)find the actor
# that may be at that position, and if there's multiple, which
# one do you use?
#
# This way, if the game supports multiple actors at the same
# position, a selection menu can be presented prior to this
# action, and that selected actor can be plumbed all the way
# through to the action behavior without losing track of it
# from only passing along its position.


class LosAction(Action):
    def __init__(self, target):
        Action.__init__(self)
        self.target = target
        self._pos = None

    def on_perform(self):
        if self._pos is None:
            self._pos = self.actor.pos.clone()
        next_step = astar(self.game, self._pos, self.target.pos)
        next_position = self._pos.plus(next_step)
        self._pos.copy(next_position)
        self.on_step(next_position)
        if next_position == self.target.pos:
            self.on_target(self.target)
            return self.succeed()
        else:
            return self.not_done()

    @abc.abstractmethod
    def on_step(self, position):
        """Called on each step of the way towards the Target."""
        pass

    @abc.abstractmethod
    def on_target(self, target):
        """Called when Target is finally reached."""
        pass


